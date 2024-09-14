from django.shortcuts import render, redirect
from django.views.generic import TemplateView, FormView, ListView
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from .models import Academia
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

from .functions import *
from core.formulas import *

from core import models as core_models
from categorias import models as categorias_models

# mantendo usuário logado
from django.contrib.auth import update_session_auth_hash


class AcademiaView(LoginRequiredMixin):
    login_url = "academias_login"

    def dispatch(self, request, *args, **kwargs):
        username = request.user.username
        academias = Academia.objects.filter(cnpj=username)
        if academias.exists():
            dias_restantes = verifica_data(academias[0].dia_expiracao)
            if dias_restantes <= 0:
                # desloga e redireciona para login de academia
                logout(request)
                messages.error(
                    request, "Sua assinatura expirou! Entre em contato com o suporte."
                )
                return redirect("academias_login")
            return super().dispatch(request, *args, **kwargs)
        else:
            # desloga e redireciona para login de academia
            logout(request)
            messages.error(request, "Academia não encontrada!")
            return redirect("academias_login")


class LoginView(TemplateView):
    template_name = "academias/login.html"

    def get(self, request, *args, **kwargs):
        # verificando se o usuário está logado
        if request.user.is_authenticated:
            return redirect("academias_index")
        else:
            return render(request, self.template_name, context=None)

    def post(self, request, *args, **kwargs):
        cnpj = request.POST.get("cnpj")
        senha = request.POST.get("senha")

        # verificando se o usuário existe
        user = authenticate(request, username=cnpj, password=senha)
        if user is not None:
            login(request, user)
            return redirect("academias_index")
        else:
            messages.error(request, "CNPJ ou senha inválidos!")
            return redirect("academias_login")


def logout_view(request):
    logout(request)
    return redirect("academias_login")


class AcademiaDashboardView(AcademiaView, TemplateView):
    template_name = "academias/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["academia"] = Academia.objects.get(cnpj=self.request.user.username)
        print("Academia: ", context["academia"].nome)
        print("Expiração: ", context["academia"].dia_expiracao)
        dias = verifica_data(context["academia"].dia_expiracao)
        print("Dias restantes: ", dias)
        context["dias"] = dias

        return context


class CadastrarAluno(AcademiaView, TemplateView):
    template_name = "academias/cadastrar_aluno.html"

    def get_context_data(self, **kwargs):
        context = {}
        context["academia"] = Academia.objects.get(cnpj=self.request.user.username)
        return context

    def post(self, request, *args, **kwargs):
        nome = request.POST.get("nome")
        username = request.POST.get("username")
        cpf = request.POST.get("cpf")
        email = request.POST.get("email")
        nascimento = request.POST.get("nascimento")
        altura = request.POST.get("altura")
        sexo = request.POST.get("sexo")
        senha1 = request.POST.get("senha1")
        senha2 = request.POST.get("senha2")
        avaliacoes = request.POST.get("avaliacoes")

        context = {
            "nome": nome,
            "username": username,
            "cpf": cpf,
            "email": email,
            "nascimento": nascimento,
            "altura": altura,
            "sexo": sexo,
            "avaliacoes": avaliacoes,
        }

        if senha1 != senha2:
            messages.error(request, "As senhas não conferem!")
            return render(request, self.template_name, context=context)

        if core_models.Usuario.objects.filter(usuario=username).exists():
            messages.error(request, "Nome de Usuário já cadastrado!")
            return render(request, self.template_name, context=context)

        if core_models.Usuario.objects.filter(email=email).exists():
            messages.error(request, "Email já cadastrado!")
            return render(request, self.template_name, context=context)

        # inserindo maskara no cpf
        cpf = f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
        if categorias_models.DadosPessoais.objects.filter(cpf=cpf).exists():
            messages.error(request, "CPF já cadastrado!")
            return render(request, self.template_name, context=context)

        if not validar_cpf(cpf):
            messages.error(request, "CPF inválido!")
            return render(request, self.template_name, context=context)

        # gerando usuário
        user = User.objects.create_user(username=username, email=email, password=senha1)
        user.save()

        data_final = calcula_data_expiracao()
        # gerando dados pessoais
        usuario = core_models.Usuario.objects.create(
            usuario=user,
            nome=nome.split(" ")[0],
            sobrenome=" ".join(nome.split(" ")[1:]),
            email=email,
            senha=senha1,
            repetir_senha=senha1,
            tipo_plano=3,
            dias_restantes=data_final,
            avaliacoes=avaliacoes,
            academia=Academia.objects.get(cnpj=self.request.user.username),
        )
        usuario.save()

        # gerando dados pessoais
        dados_pessoais = categorias_models.DadosPessoais.objects.create(
            user=username,
            sexo=sexo,
            nascimento=nascimento,
            altura=altura,
            cpf=cpf,
            nome_completo=nome,
        )
        dados_pessoais.save()

        usuario.dados_pessoais = dados_pessoais
        usuario.save()

        # tirando avalialiacoes da academia
        academia = Academia.objects.get(cnpj=self.request.user.username)
        academia.avaliacoes_disponiveis = academia.avaliacoes_disponiveis - int(
            avaliacoes
        )
        academia.save()

        messages.success(request, "Aluno cadastrado com sucesso!")

        usuario = User.objects.get(username=request.user.username)
        update_session_auth_hash(request, usuario)
        return redirect("cadastrar_aluno")


class Calculadora(AcademiaView, TemplateView):
    template_name = "academias/calculadora.html"

    def get_context_data(self, **kwargs):
        academia = Academia.objects.get(cnpj=self.request.user.username)
        context = super().get_context_data(**kwargs)
        context["academia"] = academia
        return context

    def post(self, *args, **kwargs):
        # pegando valores post
        sexo = self.request.POST.get("sexo")
        peso = float(self.request.POST.get("peso"))
        abdomen = float(self.request.POST.get("abdomen"))
        punho = float(self.request.POST.get("punho"))
        altura = float(self.request.POST.get("altura"))
        quadril = float(self.request.POST.get("quadril"))
        idade = int(self.request.POST.get("idade"))
        parte = parte_a(peso, abdomen, punho, sexo, quadril, altura)
        ga = round(gordura_atual(peso, parte, sexo), 1)
        # calcular massa_magra_real (peso - (peso * percentual_gordura_atual))
        MM_real = round(peso - (peso * ga / 100), 1)
        # pegar gordura ideal
        gordura_i = gordura_ideal(sexo, idade)

        fator_multiplicação = 1 + gordura_i / 100
        peso_ideal = round(MM_real * fator_multiplicação, 1)
        peso_gordura_ideal = round(peso_ideal - MM_real, 1)

        # gordura e peso perfeitos
        gordura_p = gordura_perfeita(sexo, idade)
        fator_multiplicação = 1 + gordura_p / 100
        peso_perfeito = round(MM_real * fator_multiplicação, 1)
        peso_gordura_perfeita = round(peso_perfeito - MM_real, 1)

        context = {
            "sem_avaliacao": self.request.GET.get("sem_avaliacao"),
            "percentual_gordura_atual": ga,
            "peso_atual": peso,
            "peso_ideal": peso_ideal,
            "peso_perfeito": peso_perfeito,
            "MM_real": MM_real,
            "peso_gordura_real": round(peso - MM_real, 1),
            "peso_gordura_ideal": round((gordura_i * MM_real) / (100 - gordura_i), 1),
            "peso_gordura_perfeita": round(
                (gordura_p * MM_real) / (100 - gordura_p), 1
            ),
            "gordura_ideal": gordura_i,
            "gordura_perfeita": gordura_p,
            "perder_bom": round(
                round(peso - MM_real, 1)
                - round((gordura_i * MM_real) / (100 - gordura_i), 1),
                2,
            ),
            "perder_perfeito": round(
                round(peso - MM_real, 1)
                - round((gordura_p * MM_real) / (100 - gordura_p), 1),
                2,
            ),
        }
        return render(self.request, "academias/calculadora.html", context)


class ConsultaAluno(AcademiaView, ListView):
    template_name = "academias/consulta_aluno_get.html"
    model = core_models.Usuario
    context_object_name = "alunos"
    paginate_by = 10
    ordering = ["nome"]


    def get_context_data(self, **kwargs):
        academia = Academia.objects.get(cnpj=self.request.user.username)
        context = super().get_context_data(**kwargs)
        context["academia"] = academia
        return context

    def get_queryset(self):
        academia = Academia.objects.get(cnpj=self.request.user.username)
        return core_models.Usuario.objects.filter(academia=academia)
    
    def post(self, *args, **kwargs):
        academia = Academia.objects.get(cnpj=self.request.user.username)
        nome = self.request.POST.get("nome")
        print("nome: ", nome)
        aluno = categorias_models.DadosPessoais.objects.filter(
            nome_completo__icontains=nome,

        )
        if aluno.exists():
            aluno = aluno.first()
            username = aluno.user
            usuario = core_models.Usuario.objects.filter(
                usuario=username, academia=academia
            )
            if not usuario.exists():
                messages.error(self.request, "Aluno ainda não finalizou o cadastro")
                return redirect("consulta_alunos")
            usuario = usuario.first()
            context = {
                "aluno": aluno,
                "usuario": usuario,
            }
            return render(self.request, "academias/consulta_aluno_post.html", context)
        else:
            messages.error(self.request, "Aluno não encontrado")
            return redirect("consulta_alunos")


class RelatorioEvolucaoAcademia(TemplateView):
    def get(self, *args, **kwargs):
        # verificando se o usuario preencheu os dados pessoais
        user = kwargs["user"]

        # verificando se o user tem mais de um plano alimentar
        planos = models.PlanoAlimentar.objects.filter(user=user)
        if planos.count() < 2:
            messages.error(
                self.request, "O Aluno não possui mais de um plano alimentar"
            )
            return redirect("consulta_alunos")

        # pegar altura do usuario
        if not categorias_models.DadosPessoais.objects.filter(user=user).exists():
            messages.error(self.request, "O Aluno não preencheu os dados pessoais")
            return redirect("consulta_alunos")
        dados_pessoais = dict(
            categorias_models.DadosPessoais.objects.filter(user=user).values()[0]
        )

        altura = dados_pessoais["altura"]

        # pegar idade do usuario
        idade = int(
            (datetime.now().date() - dados_pessoais["nascimento"]).days // 365.25
        )

        # pegar sexo do usuario
        sexo = dados_pessoais["sexo"]

        # pegar peso do usuario
        if not categorias_models.Antropometricos.objects.filter(user=user).exists():
            messages.error(
                self.request, "O Aluno não preencheu os dados antropométricos"
            )
            return redirect("consulta_alunos")
        dados_antropometricos = dict(
            categorias_models.Antropometricos.objects.filter(user=user).values()[0]
        )
        peso = dados_antropometricos["peso"]

        if not models.PlanoAlimentar.objects.filter(user=user).exists():
            messages.error(self.request, "O Aluno não possui plano alimentar")
            return redirect("consulta_alunos")
        plano = dict(
            models.PlanoAlimentar.objects.filter(user=user)
            .values()
            .order_by("data_realizacao")[0]
        )

        percentual_gordura_atual = plano["percentual_gordura"]

        # pegar percentual ideal de gordura para idade e sexo
        percentual_gordura_ideal = gordura_ideal(sexo, idade)
        # criar valores das constantes para multiplicar pela altura
        i_altura = 1.45
        i_const = 19.5
        rel_alt_const = dict()
        for i in range(100):
            rel_alt_const[f"{i_altura:.2f}"] = round(i_const, 1)
            i_altura = i_altura + 0.01
            i_const += 0.1
            i += 1

        # pegar o valor da constante que corresponde à altura do usuário
        altura_str = str(round(altura / 100, 2))
        constante = rel_alt_const[altura_str]

        # calcular peso_ideal (constante * altura**2)
        peso_ideal = round(float(constante) * float((altura / 100) ** 2), 2)
        if peso < peso_ideal - 1:
            estado_peso = "abaixo"
        elif peso > peso_ideal + 1:
            estado_peso = "acima"
        else:
            estado_peso = "na_media"
        # calcular massa_magra_ideal (peso_ideal - (peso_ideal * percentual_gordura_ideal))
        MM_ideal = round(
            peso_ideal - ((peso_ideal / 100) * percentual_gordura_ideal), 2
        )

        # calcular massa_magra_real (peso - (peso * percentual_gordura_atual))
        MM_real = round(peso - ((peso / 100) * percentual_gordura_atual), 2)
        if MM_real > MM_ideal:
            massa_magra = "acima"
        elif MM_real < MM_ideal:
            massa_magra = "baixa"
        else:
            massa_magra = "normal"

        per_gordura, estado_per_gordura = gera_estado_e_per_gordura(
            percentual_gordura_atual, idade, sexo
        )

        # pegando ultimos planos alimentares
        if not models.PlanoAlimentar.objects.filter(user=user).exists():
            messages.error(self.request, "O Aluno não possui plano alimentar")
            return redirect("consulta_alunos")
        planos = list(
            models.PlanoAlimentar.objects.filter(user=user)
            .values()
            .order_by("data_realizacao")
        )[0:1]
        quadris = []
        cinturas = []
        abdomens = []
        for plano in planos:
            cinturas.append(plano["cintura"])
            quadris.append(plano["quadril"])
            abdomens.append(plano["abdomen"])

        # criando valores dos riscos cintura
        riscos_cintura = []
        for i, cintura in enumerate(cinturas):
            riscos_cintura.append(calcula_cintura(altura, cintura))

        # criando valores risco quadril
        riscos_quadril = []
        for i, quadril in enumerate(quadris):
            riscos_quadril.append(calcula_quadril(sexo, float(quadril), float(altura)))

        # criando valores de risco abdomen
        riscos_abdomen = []
        for i, abdomen in enumerate(abdomens):
            riscos_abdomen.append(calcula_abdomen(sexo, abdomen))

        # criando valores de risco quadril cintura
        riscos_quad_cint = []
        for i, cintura in enumerate(cinturas):
            riscos_quad_cint.append(
                cintura_quadril(sexo, idade, quadris[i], cinturas[i])
            )

        # pegando o PESO AJUSTADO
        dados_pessoais = dict(
            categorias_models.DadosPessoais.objects.filter(user=user).values()[0]
        )
        # atribuindo a um dicionário "infos" os dados do usuário pertinentes à fórmula
        dados_antropometricos = dict(
            categorias_models.Antropometricos.objects.filter(user=user).values()[0]
        )
        infos = {
            "idade": int(
                (datetime.now().date() - dados_pessoais["nascimento"]).days // 365.25
            ),
            "sexo": dados_pessoais["sexo"],
            "altura": float(dados_pessoais["altura"]),
            "abdomen": float(dados_antropometricos["abdomen"]),
            "pulso": float(dados_antropometricos["pulso"]),
            "peso": float(dados_antropometricos["peso"]),
            "quadril": float(dados_antropometricos["quadril"]),
        }

        parte = parte_a(
            infos["peso"],
            infos["abdomen"],
            infos["pulso"],
            infos["sexo"],
            infos["quadril"],
            infos["altura"],
        )
        gi = gordura_ideal(infos["sexo"], infos["idade"])
        parte = parte_a(
            infos["peso"],
            infos["abdomen"],
            infos["pulso"],
            infos["sexo"],
            infos["quadril"],
            infos["altura"],
        )

        ga = gordura_atual(infos["peso"], parte, infos["sexo"])
        gi = gordura_ideal(infos["sexo"], infos["idade"])
        gm = gordura_meta(gi, ga, infos["sexo"])
        pa = peso_ajustado(float(infos["peso"]), float(ga), float(gm))

        # pegando primeiro plano alimentar
        plano_1 = list(
            models.PlanoAlimentar.objects.filter(user=user)
            .values()
            .order_by("data_realizacao")
        )[0]
        per_gor_inicial = float(plano_1["percentual_gordura"]) - float(0.3)
        # criando valores de meta da gordura
        lista_metas = dict()
        lista_metas[0] = 0
        lista_oks = dict()
        lista_oks[0] = 0
        if percentual_gordura_atual <= per_gor_inicial + 0.3:
            for i in range(80):
                lista_oks[i] = "--"

        i = 1
        while i < 80:
            lista_metas[i] = "-----"
            i += 1
        i = 1

        gm = gordura_meta(percentual_gordura_ideal, percentual_gordura_atual, sexo)
        pa = peso_ajustado(
            float(infos["peso"]), float(percentual_gordura_atual), float(gm)
        )

        while per_gor_inicial > gm:
            per_gor_inicial -= 0.3
            if percentual_gordura_atual <= per_gor_inicial:
                lista_oks[i] = "OK"
            else:
                lista_oks[i] = "--"
            lista_metas[i] = round(per_gor_inicial, 1)
            i += 1

        P7 = peso
        P8 = percentual_gordura_atual
        P9 = P7 / 100 * P8
        R9 = percentual_gordura_ideal
        R10 = 100 - R9
        P10 = P7 - P9
        S10 = P10
        S9 = R9 * S10 / R10
        peso_desejado = S9 + S10

        dados_pessoais = categorias_models.DadosPessoais.objects.filter(
            user=user
        ).values()[0]
        nome = str(dados_pessoais["nome_completo"]).split(" ")[0]
        sobrenome = nome[-1]
        context = {
            "nome_pessoa": nome,
            "sobrenome_pessoa": sobrenome,
            "peso": peso,
            "estado_peso": estado_peso,
            "massa_media": massa_magra,
            "per_gordura": per_gordura,
            "altura": round(altura / 100, 2),
            "sexo": sexo,
            "peso_ideal": round(peso_desejado, 1),
            "peso_ideal_min": int(peso_ideal) - 1,
            "peso_ideal_max": int(peso_ideal) + 1,
            "percentual_gordura_ideal": round(percentual_gordura_ideal, 1),
            "percentual_gordura_real": round(percentual_gordura_atual, 1),
            "estado_per_gordura": estado_per_gordura,
            "peso_real_gordura": round(float(peso) - float(MM_real), 1),
            "peso_ideal_gordura": round(
                float(percentual_gordura_ideal)
                * float(MM_real)
                / float(100 - float(percentual_gordura_ideal)),
                1,
            ),
            "peso_real_MM": round(MM_real, 1),
            "riscos_cintura": riscos_cintura,
            "riscos_quad_cint": riscos_quad_cint,
            "riscos_abdomen": riscos_abdomen,
            "riscos_quadril": riscos_quadril,
            "kcal_1": int(round((pa * 30) / 100) * 100),
            "kcal_2": int(plano["kcal"]),
            "kcal_3": int(plano["kcal_simples"]),
            "lista": lista_metas,
            "lista_oks": lista_oks,
        }
        if sexo == "masculino":
            self.template_name = "core/relatorio_m.html"
        else:
            self.template_name = "core/relatorio_evolucao.html"
        return render(self.request, self.template_name, context)


class EvolucaoFinal(TemplateView):
    template_name = "core/evolucao_modelo.html"

    def get(self, *args, **kwargs):
        # verificando se o usuario preencheu os dados pessoais
        user = kwargs["user"]
        if not categorias_models.DadosPessoais.objects.filter(usuario=user).exists():
            messages.error(self.request, "O Usuário não preencheu os dados pessoais")
            return redirect("consulta_alunos")

        # verificando se o usuário concluiu seu cadastro
        sexo = dict(
            categorias_models.DadosPessoais.objects.filter(user=user).values()[0]
        )["sexo"]
        altura = dict(
            categorias_models.DadosPessoais.objects.filter(user=user).values()[0]
        )["altura"]
        idade = int(
            (
                datetime.now().date()
                - dict(
                    categorias_models.DadosPessoais.objects.filter(user=user).values()[
                        0
                    ]
                )["nascimento"]
            ).days
            // 365.25
        )
        usuario = dict(models.Usuario.objects.filter(usuario=user).values()[0])

        usuario = dict(models.Usuario.objects.filter(usuario=user).values()[0])
        planos = list(
            models.PlanoAlimentar.objects.filter(user=user)
            .values()
            .order_by("data_realizacao")
        )[:6]

        # verificando se o usuário possui menos de dois planos alimentares realizados
        if len(planos) < 2:
            messages.error(self.request, "O Usuário não possui mais de um plano.")
            return redirect("consulta_alunos")
        datas_lista = [
            plano["data_realizacao"].strftime("%d/%m/%Y") for plano in planos
        ]
        datas_planos = {}
        for i in range(len(datas_lista)):
            datas_planos[f"data_{i+1}"] = datas_lista[i]

        consultas = {}
        riscos = {}
        i = 1
        for plano in planos:
            ### Consultas ###
            consultas[f"peso_{i}"] = round(
                plano["peso"], 2 if len(str(plano["peso"]).split(".")[0]) < 3 else 1
            )
            consultas[f"per_gordura_{i}"] = round(plano["percentual_gordura"], 1)
            consultas[f"massa_magra_{i}"] = round(
                float(plano["peso"]) - float(plano["gordura_corporal"]), 1
            )
            consultas[f"peso_gordura_{i}"] = round(
                plano["gordura_corporal"],
                2 if len(str(plano["gordura_corporal"]).split(".")[0]) < 2 else 1,
            )
            consultas[f"cintura_{i}"] = round(
                plano["cintura"],
                2 if len(str(plano["cintura"]).split(".")[0]) < 3 else 1,
            )
            consultas[f"abdomen_{i}"] = round(
                plano["abdomen"],
                2 if len(str(plano["abdomen"]).split(".")[0]) < 3 else 1,
            )
            consultas[f"quadril_{i}"] = round(
                plano["quadril"],
                2 if len(str(plano["quadril"]).split(".")[0]) < 3 else 1,
            )

            ### Riscos ###
            riscos[f"quadril_{i}"] = calcula_quadril(
                sexo, float(plano["quadril"]), float(altura)
            )
            riscos[f"cintura_{i}"] = calcula_cintura(altura, plano["cintura"])
            riscos[f"abdomen_{i}"] = calcula_abdomen(sexo, plano["abdomen"])
            riscos[f"cintura_quadril_{i}"] = cintura_quadril(
                sexo, idade, float(plano["quadril"]), float(plano["cintura"])
            )

            i += 1

        # Pegando Kcal
        ultimo_plano = planos[-1]

        # Comparação 2 últimos planos
        ultimos = planos[-2:]
        datas = {}
        i = 1
        for plano in ultimos:
            datas[f"data_{i}"] = plano["data_realizacao"].strftime("%d/%m/%Y")
            i += 1

        kcals = {}
        # pegando os valores caloricos
        parte = parte_a(
            planos[-1]["peso"],
            planos[-1]["abdomen"],
            planos[-1]["pulso"],
            sexo,
            planos[-1]["quadril"],
            altura,
        )
        gi = gordura_ideal(sexo, idade)
        per_gordura_atual = round(
            float(planos[-1]["percentual_gordura"]),
            2 if len(str(planos[-2]["percentual_gordura"]).split(".")[0]) < 2 else 1,
        )
        gm = gordura_meta(gi, per_gordura_atual, sexo)
        pa = peso_ajustado(
            float(planos[-1]["peso"]), float(per_gordura_atual), float(gm)
        )
        kcals["kcal_1"] = int(round((pa * 30) / 100) * 100)
        kcals["kcal_2"] = int(planos[-1]["kcal"])
        mes_realizacao = int(planos[-1]["data_realizacao"].strftime("%m"))
        meses = {
            1: "JANEIRO",
            2: "FEVEREIRO",
            3: "MARÇO",
            4: "ABRIL",
            5: "MAIO",
            6: "JUNHO",
            7: "JULHO",
            8: "AGOSTO",
            9: "SETEMBRO",
            10: "OUTUBRO",
            11: "NOVEMBRO",
            12: "DEZEMBRO",
        }
        kcals["mes"] = meses[mes_realizacao]
        # Pegando as diferenças
        diferencas = {}

        # diferenca de peso
        diferenca_peso = float(planos[-1]["peso"]) - float(planos[-2]["peso"])
        diferenca_peso = round(
            diferenca_peso, 2 if len(str(diferenca_peso).split(".")[0]) < 2 else 1
        )
        if diferenca_peso == 0:
            diferenca_peso_estado = "MANUTENCAO"
        elif 0 < diferenca_peso <= 1.5:
            diferenca_peso_estado = "AUMENTO"
        elif diferenca_peso > 1.5:
            diferenca_peso_estado = "GRANDE AUMENTO"
        elif -1.5 <= diferenca_peso < 0:
            diferenca_peso_estado = "DIMINUICAO"
        elif diferenca_peso < -1.5:
            diferenca_peso_estado = "GRANDE DIMINUICAO"
        diferenca_peso = str(abs(diferenca_peso))
        diferencas["peso"] = diferenca_peso
        diferencas["peso_descricao"] = diferenca_peso_estado

        # diferenca de % gordura
        diferenca_percentual_gordura = float(planos[-1]["percentual_gordura"]) - float(
            planos[-2]["percentual_gordura"]
        )
        diferenca_percentual_gordura = round(
            diferenca_percentual_gordura,
            2 if len(str(diferenca_percentual_gordura).split(".")[0]) < 2 else 1,
        )
        if diferenca_percentual_gordura == 0:
            diferenca_percentual_gordura_estado = "MANUTENCAO"
        elif 0 < diferenca_percentual_gordura <= 0.2:
            diferenca_percentual_gordura_estado = "LEVE AUMENTO"
        elif diferenca_percentual_gordura > 0.2:
            diferenca_percentual_gordura_estado = "AUMENTO"
        elif -0.2 <= diferenca_percentual_gordura < 0:
            diferenca_percentual_gordura_estado = "LEVE DIMINUICAO"
        elif diferenca_percentual_gordura < -0.2:
            diferenca_percentual_gordura_estado = "DIMINUICAO"
        diferenca_percentual_gordura = str(abs(diferenca_percentual_gordura))
        diferencas["percentual_gordura"] = diferenca_percentual_gordura
        diferencas["percentual_gordura_descricao"] = diferenca_percentual_gordura_estado

        # diferenca de peso da gordura
        diferenca_peso_gordura = float(planos[-1]["gordura_corporal"]) - float(
            planos[-2]["gordura_corporal"]
        )
        diferenca_peso_gordura = round(
            diferenca_peso_gordura,
            2 if len(str(diferenca_peso_gordura).split(".")[0]) < 2 else 1,
        )
        if diferenca_peso_gordura == 0:
            diferenca_peso_gordura_estado = "MANUTENCAO"
        elif diferenca_peso_gordura > 0:
            diferenca_peso_gordura_estado = "AUMENTO"
        elif -0.2 <= diferenca_peso_gordura < 0:
            diferenca_peso_gordura_estado = "LEVE DIMINUICAO"
        elif diferenca_peso_gordura < -0.2:
            diferenca_peso_gordura_estado = "DIMINUICAO"
        diferenca_peso_gordura = str(abs(diferenca_peso_gordura))
        diferencas["peso_gordura"] = diferenca_peso_gordura
        diferencas["peso_gordura_descricao"] = diferenca_peso_gordura_estado

        # diferenca de Massa Magra
        diferenca_MM = (
            float(planos[-1]["peso"]) - float(planos[-1]["gordura_corporal"])
        ) - (float(planos[-2]["peso"]) - float(planos[-2]["gordura_corporal"]))
        diferenca_MM = round(
            diferenca_MM, 2 if len(str(diferenca_MM).split(".")[0]) < 2 else 1
        )
        if diferenca_MM == 0:
            diferenca_MM_estado = "MANUTENCAO"
        elif 0 < diferenca_MM <= 0.2:
            diferenca_MM_estado = "LEVE AUMENTO"
        elif diferenca_MM > 0.2:
            diferenca_MM_estado = "AUMENTO"
        elif diferenca_MM < 0:
            diferenca_MM_estado = "DIMINUICAO"
        diferenca_MM = str(abs(diferenca_MM))
        diferencas["peso_MM"] = diferenca_MM
        diferencas["peso_MM_descricao"] = diferenca_MM_estado

        # Pegando a meta de evolução
        per_gordura_inicial = round(
            float(planos[0]["percentual_gordura"]),
            2 if len(str(planos[0]["percentual_gordura"]).split(".")[0]) < 2 else 1,
        )
        per_gordura_meta = gm

        valores = {"meta_1": per_gordura_inicial, "meta_1_estado": "OK"}
        i = 2
        for _ in range(65):
            if per_gordura_inicial >= per_gordura_meta:
                per_gordura_inicial -= 0.3
                valores[f"meta_{i}"] = round(
                    per_gordura_inicial,
                    2 if len(str(per_gordura_inicial).split(".")[0]) < 2 else 1,
                )
                if per_gordura_atual <= per_gordura_inicial:
                    valores[f"meta_{i}_estado"] = "OK"
                else:
                    valores[f"meta_{i}_estado"] = "__"
            else:
                valores[f"meta_{i}"] = "____"
                valores[f"meta_{i}_estado"] = "__"
            i += 1
        context = {
            "nome_pessoa": usuario["nome"],
            "sobrenome_pessoa": usuario["sobrenome"],
            "datas_planos": datas_planos,
            "consultas": consultas,
            "riscos": riscos,
            "datas": datas,
            "diferencas": diferencas,
            "valores": valores,
            "kcals": kcals,
        }
        return render(self.request, self.template_name, context)


# criando receiver para quando academia for criada, atualizada ou deletada
@receiver(post_save, sender=Academia)
def create_user(sender, instance, created, **kwargs):
    if created:
        user = User.objects.create_user(username=instance.cnpj, password=instance.senha)
        user.save()

    else:
        user = User.objects.get(username=instance.cnpj)
        user.set_password(instance.senha)
        user.save()


@receiver(post_delete, sender=Academia)
def delete_user(sender, instance, **kwargs):
    user = User.objects.get(username=instance.email)
    user.delete()
