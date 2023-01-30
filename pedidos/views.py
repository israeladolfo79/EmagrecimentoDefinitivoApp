from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import TemplateView
from .forms import PedidosForm, Cad
from .models import Pedidos, PacoteDeVenda
from core import models as core_models
from categorias import models as categorias_models
from django.contrib import messages, auth


from core.models import Usuario
from django.contrib.auth.models import User
from core.forms import CadastroForm
from categorias.forms import DadosPessoaisForm


class OrderCreateView(TemplateView):
    model = Pedidos
    template_name = "pedido/order_form.html"
    def get(self, *args, **kwargs):
        query = list(PacoteDeVenda.objects.all().order_by("titulo"))
        context = {
            'pacote':query[0],
            'pacotes':query[1:4],
            "lista": {0: 1, 1: 2, 2: 3,}
        }
        return render(self.request, self.template_name, context)
    def post(self, *args, **kwargs):
        usuario = self.request.user.username
        if not categorias_models.DadosPessoais.objects.filter(user=usuario).exists():
            messages.add_message(self.request, messages.SUCCESS, "Você precisa completar seus dados pessoais para contratar um pacote!")
            self.request.session['contratando'] = True
            return redirect('dados_pessoais')
        pessoa = dict(core_models.Usuario.objects.filter(usuario=usuario).values()[0])
        dados_pessoais = dict(categorias_models.DadosPessoais.objects.filter(user=usuario).values()[0])
        dados = {
                "cpf": dados_pessoais["cpf"],
                "nome": dados_pessoais["nome_completo"],
                "email": pessoa["email"],
                "preco_total": float(str(self.request.POST.get("preco_total")).replace(",", ".")),
                "pacote_de_planos": PacoteDeVenda.objects.get(id=self.request.POST.get('id')),
        }  
        form = PedidosForm(dados)
        if form.is_valid():
            order = form.save()
            self.request.session["order_id"] = order.id
            self.request.session["order_description"] = order.pacote_de_planos.descricao
            return redirect(reverse("payments:payment_method"))
        query = PacoteDeVenda.objects.all()
        context = {
            'pacotes':query
        }
        messages.add_message(self.request, messages.ERROR, "Houve um erro com a criação do pedido! Por favor, tente novamente!")
        messages.add_message(self.request, messages.ERROR, form.errors.as_ul())
        return render(self.request, self.template_name, context)


class OrderCad(TemplateView):
    template_name = "pedido/order_cad.html"
    def get(self, *args, **kwargs):
        query = list(PacoteDeVenda.objects.all().order_by("titulo"))
        pacote = query[4]
        if not pacote.ativo:
            messages.error(self.request, 'Esta promoção não está mais ativa!')
            return redirect('cadastro')
        if self.request.user.is_authenticated:
            return redirect('index')
        self.request.session['id_order'] = pacote.id
        form = Cad
        context = {
            'form': form,
            'pacote': pacote
        }
        return render(self.request, self.template_name, context)

    def post(self, request):
        form = Cad(self.request.POST or None)
        if form.is_valid():
            req = self.request.POST

            #criando usuario do sistema django
            djangouser = User.objects.create_user(
                username = req.get('usuario'),
                first_name = str(req.get('nome')).split(' ')[0],
                last_name = str(req.get('nome')).split(' ')[-1],
                password = req.get('senha'),
                email = req.get('email')
            )
            djangouser.save()

            cadastro_usuario = {
                    'usuario': req.get('usuario'),
                    'nome': str(req.get('nome')).split(' ')[0],
                    'sobrenome': str(req.get('nome')).split(' ')[1],
                    'email': req.get('email'),
                    'senha': req.get('senha'),
                    'repetir_senha': req.get('repetir_senha'),
                }
            #criando usuario do site
            userform = CadastroForm(cadastro_usuario)
            if userform.is_valid():
                userform.save()


            
                #criando os dados pessoais
                dados_pessoais = {
                    'user': req.get('usuario'),
                    'sexo': req.get('sexo'),
                    'nascimento': req.get('nascimento'),
                    'cpf': req.get('cpf'),
                    'altura': req.get('altura'),
                    'nome_completo': req.get('nome'),
                }
                form = DadosPessoaisForm(dados_pessoais)
                if form.is_valid():
                    form.save()

                    #fazer o login
                    usuario = request.POST.get('usuario')
                    senha = request.POST.get('senha')
                    user = auth.authenticate(request, username=usuario, password=senha)
                    auth.login(request, user)

                    #atribuindo o dados pessoais criados ao usuário
                    usuario = core_models.Usuario.objects.get(usuario=self.request.user)
                    usuario.dados_pessoais = categorias_models.DadosPessoais.objects.get(user=self.request.user)
                    usuario.save()
                    
                    dados = {
                        "cpf": req.get('cpf'),
                        "nome": req.get('nome'),
                        "email": req.get('email'),
                        "preco_total": float(PacoteDeVenda.objects.get(id=self.request.session['id_order']).preco),
                        "pacote_de_planos": PacoteDeVenda.objects.get(id=self.request.session['id_order']),
                    } 
                    formu = PedidosForm(dados)
                    if formu.is_valid():
                        order = formu.save()
                        self.request.session["order_id"] = order.id
                        self.request.session["order_description"] = order.pacote_de_planos.descricao
                        del self.request.session['id_order']
                        return redirect(reverse("payments:payment_method"))

        context = {
            'form': form,
            'pacote': list(PacoteDeVenda.objects.all().order_by("titulo"))[4]
            
        }
        return render(self.request, self.template_name, context)


def handler404(request, exception):
    return render(request, "notfound.html")