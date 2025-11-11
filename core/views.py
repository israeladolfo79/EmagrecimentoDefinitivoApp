from django.core.mail import EmailMultiAlternatives
from django.db.models import Q
import os
from .formulas import *
from time import sleep
from datetime import datetime, timedelta, date
from pathlib import Path
from categorias import models as categorias_models
from categorias import forms as categorias_forms
from . import models
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, ListView, DetailView
from django.contrib import messages, auth
from django.contrib.auth.models import User
from .forms import CadastroForm
from django.http import HttpResponse
import base64
import io
import PIL.Image as Image
from django.core.files.images import ImageFile
from django.template.loader import render_to_string
from weasyprint import HTML, CSS
import tempfile
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib.staticfiles import finders
import logging

import time
import tempfile
from django.conf import settings
from django.template.loader import render_to_string
from django.http import HttpResponse
from weasyprint import HTML, CSS


BASE_DIR = Path(__file__).resolve().parent.parent


def error_404(request, exception):
    return render(request, 'core/notfound.html')

def error_500(request, *args, **kwargs):
    return render(request, 'core/error_500.html')


# class Redirecionador(TemplateView):
#     template_name = ""

#     def get(self, *args, **kwargs):
#         return redirect('index')

class Index(TemplateView):
    template_name = 'core/dashboard.html'

    def get(self, *args, **kwargs):
        print("peguei usuário")
        if self.request.user.is_authenticated:
            print("usuario autenticado")
            usuario = self.request.user.username
            if not list(models.Usuario.objects.filter(usuario=usuario).values()):
                messages.add_message(
                    self.request, messages.ERROR, "Usuário não encontrado")
                return redirect('login')

            usuario = models.Usuario.objects.get(usuario=self.request.user.username)
            #se o usuário possui dados pessoais, significa que já se cadastrou
            if usuario.dados_pessoais:
                print("possui dados pessoais")
                #se o usuário se cadastrou mas não contratou um pacote, redirecinar ele para compra do pacote
                if usuario.tipo_plano == 0:
                    messages.error(self.request, "Você precisa contratar um pacote para ter acesso ao sistema.")
                    return redirect('pedidos:pedido')

                #se o usuario contratou um pacote mas não viu o video, redirecionar ele para o video
                if not usuario.assistiu_video:
                    print("redirecionando para vídeo")
                    return redirect('video_explicativo')

                #se o usuario possui pacote e viu o video, mandar ele pra dashboard cliente
                return redirect('index_2')

            context = {
                'usuario': usuario,
                'pagina': list(models.DashBoard.objects.all().values())[0],
                'sem_avaliacao': self.request.GET.get('sem_avaliacao'),
                'sem_tempo': self.request.GET.get('sem_tempo'),
            }
        else:
            context = {'pagina': list(models.DashBoard.objects.all().values())[0]}
        return render(self.request, self.template_name, context)

class Index_2(TemplateView):
    template_name = 'core/dashboard_cliente.html'

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            usuario = self.request.user.username
            if not list(models.Usuario.objects.filter(usuario=usuario).values()):
                messages.add_message(
                    self.request, messages.ERROR, "Usuário não encontrado")
                return redirect('login')
            dias_r = 0
            usuario = models.Usuario.objects.get(usuario=self.request.user)

            #caso o usuario nao possua dados pessoais
            if not usuario.dados_pessoais:
                return redirect('index')

            #caso ele possua dados pessoais
            else:

                #se o usuario precisar contratar um pacote:
                if usuario.tipo_plano == 0:
                    messages.error(self.request, "Você precisa contratar um pacote para ter acesso ao sistema.")
                    return redirect('pedidos:pedido')
                
                else:
                    if not usuario.assistiu_video:
                        return redirect('video_explicativo')
            dias_r = (datetime.strptime(usuario.dias_restantes, "%d/%m/%Y").date() - datetime.now().date()).days

                
            context = {
                'usuario': usuario,
                'pagina': list(models.DashBoard.objects.all().values())[0],
                'sem_avaliacao': self.request.GET.get('sem_avaliacao'),
                'sem_tempo': self.request.GET.get('sem_tempo'),
                'dias': dias_r
            }
        else:
            return redirect('login')
        return render(self.request, self.template_name, context)

class VideoExplicativo(TemplateView):
    template_name = "core/video_explicativo.html"

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            usuario = self.request.user.username
            if not models.Usuario.objects.filter(usuario=usuario).exists():
                messages.add_message(
                    self.request, messages.ERROR, "Usuário não encontrado")
                return redirect('login')

            video = models.Video.objects.first().link
            usuario = models.Usuario.objects.get(usuario=usuario)

            context = {
                'usuario': usuario,
                'link': video,
            }
        return render(self.request, self.template_name, context)

class VideoExplicativoConfirm(TemplateView):
    template_name = "core/video_explicativo.html"

    def get(self, *args, **kwargs):
        if not self.request.user.is_authenticated:
            messages.add_message(self.request, messages.ERROR, "Usuário não encontrado")

            return redirect('login')

        usuario = categorias_models.DadosPessoais.objects.filter(user=self.request.user.username)
        if not usuario.exists():
            messages.add_message(self.request, messages.ERROR, "Usuário não encontrado")

            return redirect('login')

        u = models.Usuario.objects.get(usuario=self.request.user.username)
        u.assistiu_video = True
        u.save()
        return redirect('index_2')

def cadastro(request):
    if request.user.is_authenticated:
        return redirect('index')
    template_name = 'core/cadastro.html'
    form = CadastroForm
    context = {
        'form': form,
    }
    if request.method == "POST":
        senha = str(request.POST.get('senha')).lower()
        senha2 = str(request.POST.get('repetir_senha')).lower()
        salvar = True
        if senha != senha2:
            salvar = False
            messages.add_message(request, messages.ERROR,
                                 "As senhas não conferem")
        if User.objects.filter(username=request.POST.get('usuario')).exists():
            salvar = False
            messages.add_message(request, messages.ERROR,
                                 "Usuário já está em uso")
        if User.objects.filter(email=request.POST.get('email')).exists():
            salvar = False
            messages.add_message(request, messages.ERROR,
                                 "Email já está em uso")
        if salvar == True:
            form = CadastroForm(request.POST)
            if form.is_valid():
                form.save()
            else:
                messages.add_message(request, messages.ERROR,
                                     "Erro ao cadastrar usuário")
                #retornando erros do formulário
                for field in form:
                    for error in field.errors:
                        messages.add_message(request, messages.ERROR, error)
                        
                return redirect('cadastro')
            usuario = User.objects.create_user(
                username=request.POST.get('usuario'),
                email=request.POST.get('email'),
                first_name=request.POST.get('nome'),
                last_name=request.POST.get('sobrenome'),
                password=request.POST.get('senha'),
            )
            usuario.save()
            messages.add_message(request, messages.SUCCESS,
                                 "Bem vindo! Agora vamos escolher seu plano Alimentar")

            usuario = request.POST.get('usuario')
            senha = request.POST.get('senha')
            user = auth.authenticate(request, username=usuario, password=senha)
            auth.login(request, user)

           

            return redirect('pedidos:pedido')
        
        context['form'] = CadastroForm(request.POST)
        
        return render(request, template_name, context)
    return render(request, template_name, context)

def Cadastro_alternativo(request):
    if request.user.is_authenticated:
        return redirect('index')
    emails_existentes = list(models.Usuario.objects.all().values())
    template_name = 'core/cadastro_alternativo.html'
    form = CadastroForm
    context = {
        'form': form,
    }
    if request.method == "POST":
        senha = str(request.POST.get('senha')).lower()
        senha2 = str(request.POST.get('repetir_senha')).lower()
        salvar = True
        if senha != senha2:
            salvar = False
            messages.add_message(request, messages.ERROR,
                                 "As senhas não conferem")
        if User.objects.filter(username=request.POST.get('usuario')).exists():
            salvar = False
            messages.add_message(request, messages.ERROR,
                                 "Usuário já está em uso")
        if User.objects.filter(email=request.POST.get('email')).exists():
            salvar = False
            messages.add_message(request, messages.ERROR,
                                 "Email já está em uso")
        if salvar == True:
            form = CadastroForm(request.POST)
            if form.is_valid():
                form.save()
            usuario = User.objects.create_user(
                username=request.POST.get('usuario'),
                email=request.POST.get('email'),
                first_name=request.POST.get('nome'),
                last_name=request.POST.get('sobrenome'),
                password=request.POST.get('senha'),
            )
            usuario.save()
            messages.add_message(request, messages.SUCCESS,
                                 "Bem vindo! Agora é só fazer seu login")
            return redirect('/login_alternativo')
        if models.PaginaInicial.objects.all().exists():
            context['pagina'] = list(
                models.PaginaInicial.objects.all().values())[0]
        else:
            context['pagina'] = None
        context['form'] = CadastroForm(request.POST)
        return render(request, template_name, context)

    if models.PaginaInicial.objects.all().exists():
        context['pagina'] = list(models.PaginaInicial.objects.all().values())[0]
    return render(request, template_name, context)

def Login(request):
    if request.user.is_authenticated:
        return redirect('index')
    if request.method != "POST":
        return render(request, 'core/login.html')
    else:
        usuario = request.POST.get('usuario')
        senha = request.POST.get('senha')
        user = auth.authenticate(request, username=usuario, password=senha)
        if not user:
            messages.add_message(request, messages.ERROR,
                                 "Usuário ou senha inválidos")
            return render(request, 'core/login.html')
        else:
            auth.login(request, user)
            return redirect('index')

def Login_alternativo(request):
    if request.user.is_authenticated:
        return redirect('index')
    if request.method != "POST":
        return render(request, 'core/login_alternativo.html', )
    else:
        usuario = request.POST.get('usuario')
        senha = request.POST.get('senha')
        user = auth.authenticate(request, username=usuario, password=senha)
        if not user:
            messages.add_message(request, messages.ERROR,
                                 "Usuário ou senha inválidos")
            return render(request, 'core/login_alternativo.html',)
        else:
            auth.login(request, user)
            return redirect('index')

def Logout(request):
    auth.logout(request)
    return redirect('/login')

# fluxo questionários
class DadosPessoais(TemplateView):
    template_name = 'core/questionarios/questionario_dados_pessoais.html'
    form = categorias_forms.DadosPessoaisForm

    def get(self, *args, **kwargs):
        usuario = models.Usuario.objects.get(usuario=self.request.user.username)
        if usuario.dados_pessoais:
            messages.add_message(self.request, messages.ERROR,
                                 "Você não pode editar seus dados pessoais")
            return redirect('/doencas')
        context = {'form': self.form, 'local': "Dados Pessoais"}
        messages.add_message(self.request, messages.ERROR,
                             "Aviso! Não será permitido a alteração de seus Dados Pessoais")
        return render(self.request, self.template_name, context)

    def post(self, *args, **kwargs):
        req = self.request.POST
        cpf = ''
        for letra in req.get('cpf'):
            if letra in '1234567890':
                cpf += letra
        dados_pessoais = {
            'user': self.request.user.username,
            'sexo': req.get('sexo'),
            'nascimento': req.get('nascimento'),
            'cpf': cpf,
            'altura': req.get('altura'),
            'nome_completo': req.get('nome_completo'),
        }
        usuario = models.Usuario.objects.get(
            usuario=self.request.user.username)
        if usuario.dados_pessoais:
            messages.add_message(self.request, messages.ERROR,
                                 "Você não pode editar seus dados pessoais")
            return redirect('/doencas')

        form = categorias_forms.DadosPessoaisForm(dados_pessoais)
        if form.is_valid():
            form.save()
            dados_pessoais = categorias_models.DadosPessoais.objects.get(
                user=self.request.user.username)
            usuario.dados_pessoais = dados_pessoais
            usuario.save()
            try:
                return redirect('pedidos:pedido')
            except:
                pass
            return redirect('doencas')
        context = {'form': form}
        messages.add_message(self.request, messages.ERROR, form.errors)
        return render(self.request, self.template_name, context)

class Questionario(TemplateView):
    template_name = 'core/questionarios/questionario.html'
    form = categorias_forms.DadosPessoaisForm
    model = categorias_models.DadosPessoais
    local = ""
    verifica_sexo = "n"

    def get(self, *args, **kwargs):
        ver = verifica_usuario(self.request.user.username)
        if not ver:
            messages.add_message(self.request, messages.ERROR, ver)
            return redirect("/?sem_tempo=1")
        else:
            pass
        if list(categorias_models.DadosPessoais.objects.filter(usuario=self.request.user.username).values()) == []:
            messages.add_message(self.request, messages.ERROR,
                                 'Você precisa preencher seus dados pessoais antes de acessar outras categorias.')
            return redirect('/dados_pessoais')

        if self.model != "":
            if len(list(self.model.objects.filter(user=self.request.user.username).values())) != 0:
                initial = list(self.model.objects.filter(
                    user=self.request.user.username).values())[0]
            else:
                initial = ""
        sexo = dict(categorias_models.DadosPessoais.objects.filter(
            usuario=self.request.user.username).values()[0])['sexo']
        if self.verifica_sexo == "s":
            if sexo != "feminino":
                return redirect("/dados_atropometricos")
        context = {"form": self.form(
            initial=initial), "local": self.local, 'sexo': sexo, "initial": initial}
        return render(self.request, self.template_name, context)

class Doenca(Questionario):
    template_name = 'core/questionarios/questionario_doencas.html'
    form = categorias_forms.DoencaForm
    model = categorias_models.Doenca
    local = "Doenças"

    def post(self, *args, **kwargs):
        req = self.request.POST
        doencas = {
            'refluxo': req.get('refluxo'),
            'gastrite': req.get('gastrite'),
            'figado': req.get('figado'),
            'renal': req.get('renal'),
            'tireoide': req.get('tireoide'),
            'pressao_alta': req.get('pressao_alta'),
            'diabetes': req.get('diabetes'),
            'colesterol': req.get('colesterol'),
            'infos_adicionais': req.get('infos_adicionais'),
        }

        obj, created = categorias_models.Doenca.objects.update_or_create(
            user=self.request.user.username,
            defaults=doencas
        )
        doenca = categorias_models.Doenca.objects.get(
            user=self.request.user.username)
        usuario = models.Usuario.objects.get(
            usuario=self.request.user.username)
        usuario.doencas = doenca
        usuario.save()
        return redirect('medicamentos')

class Medicamento(Questionario):
    template_name = 'core/questionarios/questionario_medicamentos.html'
    form = categorias_forms.MedicamentoForm
    model = categorias_models.Medicamento
    local = "Medicamentos"

    def post(self, *args, **kwargs):
        req = self.request.POST
        medicamentos = {
            'medicamentos': req.get('medicamentos'),
            'medicamentos_utilizados': req.get('medicamentos_utilizados'),
            'infos_adicionais': req.get('infos_adicionais'),
        }
        obj, created = categorias_models.Medicamento.objects.update_or_create(
            user=self.request.user.username,
            defaults=medicamentos
        )
        medicamento = categorias_models.Medicamento.objects.get(
            user=self.request.user.username)
        usuario = models.Usuario.objects.get(
            usuario=self.request.user.username)
        usuario.medicamentos = medicamento
        usuario.save()
        return redirect('/exame_de_sangue')

class ExameDeSangue(Questionario):
    template_name = 'core/questionarios/questionario_exame_sangue.html'
    form = categorias_forms.ExameSangueForm
    model = categorias_models.ExameSangue
    local = "Exame de Sangue"

    def post(self, *args, **kwargs):
        req = self.request.POST
        dados = {
            'exame': req.get('exame'),
            'alteracoes': req.get('alteracoes'),
            'infos_adicionais': req.get('infos_adicionais'),
        }
        obj, created = categorias_models.ExameSangue.objects.update_or_create(
            user=self.request.user.username,
            defaults=dados
        )
        dado = categorias_models.ExameSangue.objects.get(
            user=self.request.user.username)
        usuario = models.Usuario.objects.get(
            usuario=self.request.user.username)
        usuario.exame_sangue = dado
        usuario.save()
        return redirect('/intestino')

class Intestino(Questionario):
    template_name = 'core/questionarios/questionario_intestino.html'
    form = categorias_forms.IntestinoForm
    model = categorias_models.Intestino
    local = 'Intestino'

    def post(self, *args, **kwargs):
        req = self.request.POST
        dados = {
            'cor_urina': req.get('cor_urina'),
            'fezes': req.get('fezes'),
            'banheiro': req.get('banheiro'),
            'infos_adicionais': req.get('infos_adicionais'),
        }
        obj, created = categorias_models.Intestino.objects.update_or_create(
            user=self.request.user.username,
            defaults=dados
        )
        dado = categorias_models.Intestino.objects.get(
            user=self.request.user.username)
        usuario = models.Usuario.objects.get(
            usuario=self.request.user.username)
        usuario.intestino = dado
        usuario.save()
        return redirect('/sono')

class Sono(Questionario):
    template_name = 'core/questionarios/questionario_sono.html'
    form = categorias_forms.SonoForm
    model = categorias_models.Sono
    local = 'Sono'

    def post(self, *args, **kwargs):
        req = self.request.POST
        dados = {
            'acorda_noite': req.get('acorda_noite'),
            'vezes_acorda_noite': int(req.get('vezes_acorda_noite')),
            'acorda_noite_banheiro': req.get('acorda_noite_banheiro'),
            'horas_sono': req.get('horas_sono'),
            'despertar': req.get('despertar'),
            'infos_adicionais': req.get('infos_adicionais'),
        }
        obj, created = categorias_models.Sono.objects.update_or_create(
            user=self.request.user.username,
            defaults=dados
        )
        dado = categorias_models.Sono.objects.get(
            user=self.request.user.username)
        usuario = models.Usuario.objects.get(
            usuario=self.request.user.username)
        usuario.sono = dado
        usuario.save()

        return redirect('/cirurgia')

class Cirurgia(Questionario):
    template_name = 'core/questionarios/questionario_cirurgias.html'
    form = categorias_forms.CirurgiaForm
    model = categorias_models.Cirurgia
    local = 'Cirurgias'

    def post(self, *args, **kwargs):
        req = self.request.POST
        dados = {
            'cirurgias': req.get('cirurgias'),
            'infos_adicionais': req.get('infos_adicionais'),
        }
        obj, created = categorias_models.Cirurgia.objects.update_or_create(
            user=self.request.user.username,
            defaults=dados
        )
        dado = categorias_models.Cirurgia.objects.get(
            user=self.request.user.username)
        usuario = models.Usuario.objects.get(
            usuario=self.request.user.username)
        usuario.cirurgias = dado
        usuario.save()

        return redirect('/alcool')

class Alcool(Questionario):
    template_name = 'core/questionarios/questionario_alcool.html'
    form = categorias_forms.AlcoolForm
    model = categorias_models.Alcool
    local = "Álcool"

    def post(self, *args, **kwargs):
        req = self.request.POST
        dados = {
            'consome_alcool': req.get('consome_alcool'),
            'quantidade_vezes': req.get('quantidade_vezes'),
            'infos_adicionais': req.get('infos_adicionais'),
        }
        obj, created = categorias_models.Alcool.objects.update_or_create(
            user=self.request.user.username,
            defaults=dados
        )
        dado = categorias_models.Alcool.objects.get(
            user=self.request.user.username)
        usuario = models.Usuario.objects.get(
            usuario=self.request.user.username)
        usuario.alcool = dado
        usuario.save()
        return redirect('/suplementos')

class Suplementos(Questionario):
    template_name = 'core/questionarios/questionario_suplementos.html'
    form = categorias_forms.SuplementoForm
    model = categorias_models.Suplemento
    local = "Suplementos"

    def post(self, *args, **kwargs):
        req = self.request.POST
        dados = {
            'creatina': req.get('creatina'),
            'termogenico': req.get('termogenico'),
            'omega_3': req.get('omega_3'),
            'vitamina_d': req.get('vitamina_d'),
            'multivitaminico': req.get('multivitaminico'),
            'proteina': req.get('proteina'),
            'maltodextrina': req.get('maltodextrina'),
            'outros': req.get('outros'),
            'infos_adicionais': req.get('infos_adicionais'),
        }
        obj, created = categorias_models.Suplemento.objects.update_or_create(
            user=self.request.user.username,
            defaults=dados
        )
        dado = categorias_models.Suplemento.objects.get(
            user=self.request.user.username)
        usuario = models.Usuario.objects.get(
            usuario=self.request.user.username)
        usuario.suplementos = dado
        usuario.save()
        return redirect('/ciclos_menstruais')

class CiclosMenstruais(Questionario):
    template_name = 'core/questionarios/questionario_ciclos_menstruais.html'
    form = categorias_forms.CicloMenstrualForm
    model = categorias_models.CicloMenstrual
    local = "Ciclos Menstruais"
    verifica_sexo = "s"

    def post(self, *args, **kwargs):
        dados_pessoais = categorias_models.DadosPessoais.objects.get(
            usuario=self.request.user.username)
        if dados_pessoais.sexo == 'masculino':
            return redirect('/dados_atropometricos')
        req = self.request.POST
        dados = {
            'quantos_dias_menstrua': req.get('quantos_dias_menstrua'),
            'quantos_dias_ciclo': req.get('quantos_dias_ciclo'),
            'ciclo': req.get('ciclo'),
            'infos_adicionais': req.get('infos_adicionais'),
        }
        obj, created = categorias_models.CicloMenstrual.objects.update_or_create(
            user=self.request.user.username,
            defaults=dados
        )
        dado = categorias_models.CicloMenstrual.objects.get(
            user=self.request.user.username)
        usuario = models.Usuario.objects.get(
            usuario=self.request.user.username)
        usuario.ciclo_menstrual = dado
        usuario.save()
        return redirect('/dados_atropometricos')

class DadosAntropometricos(Questionario):
    template_name = 'core/questionarios/questionario_dados_antropometricos.html'
    form = categorias_forms.AntropometricosForm
    model = categorias_models.Antropometricos
    local = "Dados Antropométricos"

    def post(self, *args, **kwargs):
        req = self.request.POST
        dados = {
            'pescoco': req.get('pescoco'),
            'cintura': req.get('cintura'),
            'quadril': req.get('quadril'),
            'pulso': req.get('pulso'),
            'abdomen': req.get('abdomen'),
            'peso': req.get('peso'),
            'infos_adicionais': req.get('infos_adicionais'),
        }
        if dict(categorias_models.DadosPessoais.objects.filter(user=self.request.user.username).values()[0])["sexo"] == "feminino":
            dados["pulso"] = 0
        obj, created = categorias_models.Antropometricos.objects.update_or_create(
            user=self.request.user.username,
            defaults=dados
        )
        dado = categorias_models.Antropometricos.objects.get(
            user=self.request.user.username)
        usuario = models.Usuario.objects.get(
            usuario=self.request.user.username)
        usuario.dados_atropometricos = dado
        usuario.save()
        return redirect('/horarios')

class Horarios(Questionario):
    template_name = 'core/questionarios/questionario_horarios.html'
    form = categorias_forms.HorariosForm
    model = categorias_models.Horarios
    local = "Horários"

    def post(self, *args, **kwargs):
        req = self.request.POST
        dados = {
            'treino': req.get('treino',),
            'acordar': req.get('acordar'),
            'cafe_da_manha': req.get('cafe_da_manha'),
            'infos_adicionais': req.get('infos_adicionais'),
        }
        if dados['treino'] == '':
            dados['treino'] = '00:00'
        if req.get('lanche_manha'):
            dados['lanche_manha'] = req.get('lanche_manha')
        if req.get('almoco'):
            dados['almoco'] = req.get('almoco')
        if req.get('lanche_tarde_1'):
            dados['lanche_tarde_1'] = req.get('lanche_tarde_1')
        if req.get('lanche_tarde_2'):
            dados['lanche_tarde_2'] = req.get('lanche_tarde_2')
        if req.get('jantar'):
            dados['jantar'] = req.get('jantar')
        if req.get('dormir'):
            dados['dormir'] = req.get('dormir')
        obj, created = categorias_models.Horarios.objects.update_or_create(
            user=self.request.user.username,
            defaults=dados
        )
        dado = categorias_models.Horarios.objects.get(
            user=self.request.user.username)
        usuario = models.Usuario.objects.get(
            usuario=self.request.user.username)
        usuario.horarios = dado
        usuario.save()
        return redirect('/exercicios')

class Exercicios(Questionario):
    template_name = 'core/questionarios/questionario_exercicios.html'
    form = categorias_forms.ExerciciosForm
    model = categorias_models.Exercicios
    local = "Exercícios"

    def post(self, *args, **kwargs):
        req = self.request.POST
        dados = {
            'treino': req.get('treino'),
            'tempo_exercicio': req.get('tempo_exercicio'),
            'treino_secundario': req.get('treino_secundario'), 
            'tempo_exercicio_secundario': req.get('tempo_exercicio_secundario'),
            'infos_adicionais': req.get('infos_adicionais'),
        }

        print("📌 POST recebido:", dict(req))
        print("📦 Dados que vão para update_or_create:", dados)

        obj, created = categorias_models.Exercicios.objects.update_or_create(
            user=self.request.user.username,
            defaults=dados
        )

        dado = categorias_models.Exercicios.objects.get(user=self.request.user.username)
        usuario = models.Usuario.objects.get(usuario=self.request.user.username)
        usuario.exercicios = dado
        usuario.save()

        messages.add_message(self.request, messages.SUCCESS, "Dados atualizados com sucesso!")
        return redirect('/confirmacao')

class RedirecionadorAvaliacao(TemplateView):
    template_name='core/avaliacao'
    def get(self, *args, **kwargs):
        avaliacoes = dict(models.Usuario.objects.filter(usuario=self.request.user.username).values()[0])['avaliacoes']
        if avaliacoes < 1:
            messages.error(self.request, "Você não possui avaliações disponíveis, Por favor contrate um novo pacote e tente novamente.")
            return redirect('/?sem_avaliacao=True')
        else:
            return redirect('/dados_pessoais')

class Avaliacao(TemplateView):
    template_name = 'core/avaliacao.html'

    def get(self, *args, **kwargs):
        # verificando se o usuario preencheu os dados pessoais
        user = self.request.user.username
        if dict(models.Usuario.objects.filter(usuario=user).values()[0])['dados_pessoais_id'] == None:
            messages.add_message(self.request, messages.ERROR,
                                 "É necessário que você responda todas as perguntas com ATENÇÃO, para no final, ter seus Planos Alimentares Personalizados")
            return redirect('/dados_pessoais')
        # verificando se o usuário concluiu seu cadastro
        sexo = dict(categorias_models.DadosPessoais.objects.filter(
            user=user).values()[0])["sexo"]
        usuario = dict(models.Usuario.objects.filter(usuario=user).values()[0])
        for k, v in usuario.items():
            if sexo == 'masculino':
                if v == None and (k != 'ciclo_menstrual_id' and k != "plano_alimentar_id"):
                    categoria_faltante = str(k).split('_')[0]
                    messages.add_message(
                        self.request, messages.ERROR, f"É necessário que você responda todas as perguntas com ATENÇÃO, para no final, ter seus Planos Alimentares Personalizados. Preencha: {categoria_faltante}")
                    return redirect('/doencas')
            else:
                if v == None and k != "plano_alimentar_id":
                    categoria_faltante = str(k).split('_')[0]
                    messages.add_message(
                        self.request, messages.ERROR, f"É necessário que você responda todas as perguntas com ATENÇÃO, para no final, ter seus Planos Alimentares Personalizados. Preencha: {categoria_faltante}")
                    return redirect('/doencas')
        # verificando se o usuário tem avaliações disponíveis
        avaliacoes = dict(models.Usuario.objects.filter(usuario=user).values()[0])['avaliacoes']
        if avaliacoes < 1:
            messages.error(self.request, "Você não possui avaliações disponíveis, Por favor contrate um novo pacote e tente novamente.")
            return redirect('/?sem_avaliacao=True')

        ver = verifica_usuario(user)
        if not ver:
            messages.add_message(self.request, messages.ERROR, ver)
            return redirect("/?sem_tempo=1")
        else:
            pass

        usuario = models.Usuario.objects.get(
            usuario=self.request.user.username)
        usuario.avaliacoes = avaliacoes - 1
        usuario.save()
        dados_pessoais = dict(
            categorias_models.DadosPessoais.objects.filter(user=user).values()[0])
        # atribuindo a um dicionário "infos" os dados do usuário pertinentes à fórmula
        dados_antropometricos = dict(
            categorias_models.Antropometricos.objects.filter(usuario=user).values()[0])
        exercicios = dict(categorias_models.Exercicios.objects.filter(
            usuario=user).values()[0])
        horarios = dict(categorias_models.Horarios.objects.filter(
            usuario=user).values()[0])
        infos = {
            'idade': int((datetime.now().date() - dados_pessoais['nascimento']).days // 365.25),
            'sexo': dados_pessoais['sexo'],
            'altura': float(dados_pessoais['altura']),
            'abdomen': float(dados_antropometricos['abdomen']),
            'pulso': float(dados_antropometricos['pulso']),
            'peso': float(dados_antropometricos['peso']),
            'quadril': float(dados_antropometricos['quadril'])
        }

        parte = parte_a(infos['peso'], infos['abdomen'], infos['pulso'],
                        infos['sexo'], infos['quadril'], infos['altura'])

        ga = gordura_atual(infos['peso'], parte, infos['sexo'])
        gi = gordura_ideal(infos["sexo"], infos['idade'])
        gm = gordura_meta(gi, ga, infos["sexo"])
        pa = peso_ajustado(float(infos['peso']), float(ga), float(gm))
        variaveis = list(models.Variaveis.objects.all().values())[0]

        # kcal = calorias_sem_treino(infos['sexo'], infos['altura'], infos['peso'], pa, infos['idade'], variavel_1=variaveis['var_1'], variavel_2=variaveis['var_2'],
        #                            variavel_3=variaveis['var_3'], variavel_4=variaveis['var_4'], variavel_5=variaveis['var_5'], variavel_6=variaveis['var_6'])
        # kcal_simples = kcal
        # treino = 'n'
        # if float(exercicios['treino']) != 0.0:
        #     treino = 's'
        #     kcal = calorias_com_treino(kcal, float(
        #         exercicios['treino']), pa, exercicios['tempo_exercicio'])
        #     if float(exercicios["treino_secundario"]):
        #         kcal = cal_com_treino_duplo(kcal, float(
        #             exercicios["treino_secundario"]), pa, exercicios['tempo_exercicio_secundario'])
        
        kcal = calorias_sem_treino(
        infos['sexo'], infos['altura'], infos['peso'], pa, infos['idade'],
        variavel_1=variaveis['var_1'], variavel_2=variaveis['var_2'],
        variavel_3=variaveis['var_3'], variavel_4=variaveis['var_4'],
        variavel_5=variaveis['var_5'], variavel_6=variaveis['var_6']
        )
        kcal_simples = kcal

        print(f"⚪ Kcal SEM TREINO: {kcal:.2f}")

        treino = 'n'
        if float(exercicios['treino']) != 0.0:
            treino = 's'
            kcal = calorias_com_treino(kcal, float(
                exercicios['treino']), pa, exercicios['tempo_exercicio'])
            print(f"🔹 Kcal COM 1 TREINO: {kcal:.2f}")

            if float(exercicios["treino_secundario"]):
                kcal = cal_com_treino_duplo(kcal, float(
                    exercicios["treino_secundario"]), pa, exercicios['tempo_exercicio_secundario'])
                print(f"🔸 Kcal COM 2 TREINOS: {kcal:.2f}")
        else:
            print("⚠️ Nenhum treino informado — permanece Kcal base.")
        
        
        
        # criando o plano alimentar
        
        plano = {
            'user': self.request.user.username,
            'pescoco': dados_antropometricos['pescoco'],
            'cintura': dados_antropometricos['cintura'],
            'quadril': dados_antropometricos['quadril'],
            'pulso': dados_antropometricos['pulso'],
            'abdomen': dados_antropometricos['abdomen'],
            'peso': dados_antropometricos['peso'],
            'percentual_gordura': ga,
            'gordura_corporal': float(ga/100) * float(dados_antropometricos['peso']),
            'treino': treino,
            'horario_treino': horarios['treino'],
            'café_da_manha': horarios['cafe_da_manha'],
            'almoco': horarios['almoco'],
            'lanche_1': horarios['lanche_manha'],
            'lanche_2': horarios['lanche_tarde_1'],
            'lanche_3': horarios['lanche_tarde_2'],
        }
        plano_alimentar = models.PlanoAlimentar(
            user=plano['user'],
            pescoco=plano['pescoco'],
            cintura=plano['cintura'],
            quadril=plano['quadril'],
            pulso=plano['pulso'],
            abdomen=plano['abdomen'],
            peso=plano['peso'],
            percentual_gordura=plano['percentual_gordura'],
            gordura_corporal=plano['gordura_corporal'],
            treino=plano['treino'],
            horario_treino=plano['horario_treino'],
            café_da_manha=plano['café_da_manha'],
            almoco=plano['almoco'],
            data_realizacao=datetime.now(),
            kcal=round(kcal/100)*100,
            kcal_simples=round(kcal_simples/100)*100,
            lanche_1=horarios['lanche_manha'],
            lanche_2=horarios['lanche_tarde_1'],
            lanche_3=horarios['lanche_tarde_2'],
            horario_janta=horarios["jantar"]
        )
        plano_alimentar.save()
        return redirect('/meus_planos_alimentares')

class ExibeAvaliacaoTreino(TemplateView):
    template_name = "core/pdf.html"

    def get(self, *args, **kwargs):
        
        # verificando se o usuario preencheu os dados pessoais
        if self.request.GET.get('username'):
            user = self.request.GET.get('username')
        elif self.request.user.username:
            user = self.request.user.username
        else:
            messages.add_message(self.request, messages.ERROR, "Você precisa enviar um formulário")
            return redirect('/dados_pessoais')
        if dict(models.Usuario.objects.filter(usuario=user).values()[0])['dados_pessoais_id'] == None:
            messages.add_message(self.request, messages.ERROR,
                                 "É necessário que você responda todas as perguntas com ATENÇÃO, para no final, ter seus Planos Alimentares Personalizados")
            return redirect('/dados_pessoais')
        
        avaliacao_mais_recente = list(
            models.PlanoAlimentar.objects.filter(user=user).values())[-1]

        usuario = dict(categorias_models.DadosPessoais.objects.filter(
            usuario=user).values()[0])
        
        usuario_obj = models.Usuario.objects.get(usuario=user)

        data_realizacao = avaliacao_mais_recente["data_realizacao"]
        data_formatada = data_realizacao.strftime("%d/%m/%Y")

        # verificando se o usuário concluiu seu cadastro
        sexo = dict(categorias_models.DadosPessoais.objects.filter(
            user=user).values()[0])["sexo"]
        usuario = dict(models.Usuario.objects.filter(usuario=user).values()[0])
        for k, v in usuario.items():
            if sexo == 'masculino':
                if v == None and k != 'ciclo_menstrual_id':
                    categoria_faltante = str(k).split('_')[0]
                    messages.add_message(
                        self.request, messages.ERROR, f"É necessário que você responda todas as perguntas com ATENÇÃO, para no final, ter seus Planos Alimentares Personalizados. Preencha: {categoria_faltante}")
                    return redirect('/dados_pessoais')
            else:
                if v == None:
                    categoria_faltante = str(k).split('_')[0]
                    messages.add_message(
                        self.request, messages.ERROR, f"É necessário que você responda todas as perguntas com ATENÇÃO, para no final, ter seus Planos Alimentares Personalizados. Preencha: {categoria_faltante}")
                    return redirect('/dados_pessoais')

        # verificando se o usuário possui plano alimentar
        if list(models.PlanoAlimentar.objects.filter(user=user).values()) == []:
            messages.add_message(self.request, messages.ERROR,
                                 "Você precisa realizar uma avaliação antes de vizualizá-lo")
            return redirect('/dados_pessoais')

        ver = verifica_usuario(user)
        if not ver:
            messages.add_message(self.request, messages.ERROR, ver)
            return redirect("/?sem_tempo=1")
        else:
            pass

        avaliacao_mais_recente = list(
            models.PlanoAlimentar.objects.filter(user=user).values())[-1]
        treino_cedo = False
        if avaliacao_mais_recente['horario_treino'] < avaliacao_mais_recente['café_da_manha']:
            treino_cedo = True
        usuario = dict(categorias_models.DadosPessoais.objects.filter(
            usuario=user).values()[0])
        criar_pa_sem_treino = True
        if avaliacao_mais_recente['treino'] == 'n':
            criar_pa_sem_treino = False

  
        usuario_obj = models.Usuario.objects.get(usuario=user)

        context = {            
            'nome_completo': f"{usuario_obj.nome} {usuario_obj.sobrenome}",
            'treino': avaliacao_mais_recente['treino'],
            'treino_cedo': treino_cedo,
            'kcal': avaliacao_mais_recente['kcal'],
            'cafe_da_manha': avaliacao_mais_recente['café_da_manha'],
            'almoco': avaliacao_mais_recente['almoco'],
            'lanche_1': avaliacao_mais_recente['lanche_1'],
            'lanche_2': avaliacao_mais_recente['lanche_2'],
            'lanche_3': avaliacao_mais_recente['lanche_3'],
            'jantar': avaliacao_mais_recente['horario_janta'],
            'criar_pa_sem_treino': criar_pa_sem_treino,
            "data_realizacao": avaliacao_mais_recente["data_realizacao"],
            "username": user,
            "tipo_plano": "avaliacao_com_treino",
            "data_realizacao": data_formatada,
        }
        
        return render(self.request, self.template_name, context)

class ExibeAvaliacaoSemTreino(TemplateView):
    template_name = "core/pdf.html"

    def get(self, *args, **kwargs):
        # verificando se o usuario preencheu os dados pessoais
        if self.request.GET.get('username'):
            user = self.request.GET.get('username')
        elif self.request.user.username:
            user = self.request.user.username
        else:
            messages.add_message(self.request, messages.ERROR, "Você precisa enviar um formulário")
            return redirect('/dados_pessoais')
        if dict(models.Usuario.objects.filter(usuario=user).values()[0])['dados_pessoais_id'] == None:
            messages.add_message(self.request, messages.ERROR,
                                 "Você precisa concluir todo o seu cadastro para poder visualizar suas informações")
            return redirect('/dados_pessoais')
        # verificando se o usuário concluiu seu cadastro
        avaliacao_mais_recente = list(
            models.PlanoAlimentar.objects.filter(user=user).values())[-1]

        usuario = dict(categorias_models.DadosPessoais.objects.filter(
            usuario=user).values()[0])
        
        usuario_obj = models.Usuario.objects.get(usuario=user)

        data_realizacao = avaliacao_mais_recente["data_realizacao"]
        data_formatada = data_realizacao.strftime("%d/%m/%Y")
        sexo = dict(categorias_models.DadosPessoais.objects.filter(
            user=user).values()[0])["sexo"]
        usuario = dict(models.Usuario.objects.filter(usuario=user).values()[0])
        for k, v in usuario.items():
            if sexo == 'masculino':
                if v == None and k != 'ciclo_menstrual_id':
                    categoria_faltante = str(k).split('_')[0]
                    messages.add_message(
                        self.request, messages.ERROR, f"É necessário que você responda todas as perguntas com ATENÇÃO, para no final, ter seus Planos Alimentares Personalizados. Preencha: {categoria_faltante}")
                    return redirect('/doencas')
            else:
                if v == None:
                    categoria_faltante = str(k).split('_')[0]
                    messages.add_message(
                        self.request, messages.ERROR, f"É necessário que você responda todas as perguntas com ATENÇÃO, para no final, ter seus Planos Alimentares Personalizados. Preencha: {categoria_faltante}")
                    return redirect('/doencas')

        if list(models.PlanoAlimentar.objects.filter(user=user).values()) == []:
            messages.add_message(self.request, messages.ERROR,
                                 "Você precisa realizar uma avaliação antes de vizualizá-la")
            return redirect('/avaliacao')

        ver = verifica_usuario(user)
        if not ver:
            messages.add_message(self.request, messages.ERROR, ver)
            return redirect("/?sem_tempo=1")
        else:
            pass

        avaliacao_mais_recente = list(
            models.PlanoAlimentar.objects.filter(user=user).values())[-1]
        usuario = dict(categorias_models.DadosPessoais.objects.filter(
            usuario=user).values()[0])
        
        usuario_obj = models.Usuario.objects.get(usuario=user)
        context = {
            'nome_completo': f"{usuario_obj.nome} {usuario_obj.sobrenome}",
            'treino': 'n',
            'treino_cedo': False,
            'kcal': avaliacao_mais_recente['kcal_simples'],
            'cafe_da_manha': avaliacao_mais_recente['café_da_manha'],
            'almoco': avaliacao_mais_recente['almoco'],
            'lanche_1': avaliacao_mais_recente['lanche_1'],
            'lanche_2': avaliacao_mais_recente['lanche_2'],
            'lanche_3': avaliacao_mais_recente['lanche_3'],
            "data_realizacao": avaliacao_mais_recente["data_realizacao"],
            "username": user,
            "tipo_plano": "avaliacao_sem_treino",
            "data_realizacao": data_formatada,
        }
        return render(self.request, self.template_name, context)

class UserInfos(TemplateView):
    template_name = "core/dados_usuario.html"

    def get(self, *args, **kwargs):
        # verificando se o usuario preencheu os dados pessoais
        user = self.request.user.username
        if dict(models.Usuario.objects.filter(usuario=user).values()[0])['dados_pessoais_id'] == None:
            messages.add_message(self.request, messages.ERROR,
                                 "Você precisa concluir todo o seu cadastro para poder visualizar suas informações")
            return redirect('/dados_pessoais')
        # verificando se o usuário concluiu seu cadastro
        sexo = dict(categorias_models.DadosPessoais.objects.filter(
            user=user).values()[0])["sexo"]
        usuario = dict(models.Usuario.objects.filter(usuario=user).values()[0])
        for k, v in usuario.items():
            if sexo == 'masculino':
                if v == None and k != 'ciclo_menstrual_id':
                    categoria_faltante = str(k).split('_')[0]
                    messages.add_message(
                        self.request, messages.ERROR, f"É necessário que você responda todas as perguntas com ATENÇÃO, para no final, ter seus Planos Alimentares Personalizados. Preencha: {categoria_faltante}")
                    return redirect('/dados_pessoais')
            else:
                if v == None:
                    categoria_faltante = str(k).split('_')[0]
                    messages.add_message(
                        self.request, messages.ERROR, f"É necessário que você responda todas as perguntas com ATENÇÃO, para no final, ter seus Planos Alimentares Personalizados. Preencha: {categoria_faltante}")
                    return redirect('/dados_pessoais')
        doencas = dict(categorias_models.Doenca.objects.filter(
            usuario=user).values()[0])
        medicamentos = dict(
            categorias_models.Medicamento.objects.filter(usuario=user).values()[0])
        exame_de_sangue = dict(
            categorias_models.ExameSangue.objects.filter(usuario=user).values()[0])
        intestino = dict(categorias_models.Intestino.objects.filter(
            usuario=user).values()[0])
        sono = dict(categorias_models.Sono.objects.filter(
            usuario=user).values()[0])
        cirurgias = dict(categorias_models.Cirurgia.objects.filter(
            usuario=user).values()[0])
        alcool = dict(categorias_models.Alcool.objects.filter(
            usuario=user).values()[0])
        suplementos = dict(categorias_models.Suplemento.objects.filter(
            usuario=user).values()[0])
        ciclo_menstrual = ''
        if sexo != "masculino":
            ciclo_menstrual = dict(
                categorias_models.CicloMenstrual.objects.filter(usuario=user).values()[0])
        dados_antropometricos = dict(
            categorias_models.Antropometricos.objects.filter(usuario=user).values()[0])
        horarios = dict(categorias_models.Horarios.objects.filter(
            usuario=user).values()[0])
        exercicios = dict(categorias_models.Exercicios.objects.filter(
            usuario=user).values()[0])
        dados_pessoais = dict(
            categorias_models.DadosPessoais.objects.filter(usuario=user).values()[0])
        context = {
            'dados_pessoais': dados_pessoais,
            'doencas': doencas,
            'medicamentos': medicamentos,
            'exame_sangue': exame_de_sangue,
            'intestino': intestino,
            'cirurgias': cirurgias,
            'sono': sono,
            'alcool': alcool,
            'suplementos': suplementos,
            'ciclo_menstrual': ciclo_menstrual,
            'antropometricos': dados_antropometricos,
            'horarios': horarios,
            'exercicios': exercicios,
        }
        return render(self.request, self.template_name, context)

class Confirmacao(TemplateView):
    template_name = "core/confirmacao.html"

class MaterialApoio(ListView):
    template_name = "core/material_apoio.html"

    def get(self, *args, **kwargs):
        usuario = self.request.user.username
        plano = list(models.Usuario.objects.filter(usuario=usuario).values())[0]
        if models.PlanoAlimentar.objects.filter(user=usuario).count() == 0:
            messages.error(self.request, "Você precisa realizar um plano alimentar para ter acesso aos materiais de apoio")
            return redirect('index')
        pacote_certo = plano["tipo_plano"]
        if pacote_certo == 0:
            liberar_especifico = "NA"
        elif pacote_certo == 1:
            liberar_especifico = "NP"
        else:
            liberar_especifico = verifica_plano_alimentar(usuario)

        context = {
            'materiais': models.MaterialDeApoio.objects.all(),
            'categorias': models.CategoriaMaterialDeApoio.objects.all(),
            'usuario': plano,
            "liberar": liberar_especifico
        }
        return render(self.request, self.template_name, context)

class CategoriaMaterialApoio(ListView):
    template_name = "core/material_apoio_categoria.html"

    def get(self, *args, **kwargs):
        categoria = self.kwargs.get('categoria', None)
        usuario = self.request.user.username
        if models.PlanoAlimentar.objects.filter(user=usuario).count() == 0:
            messages.error(self.request, "Você precisa realizar um plano alimentar para ter acesso aos materiais de apoio")
            return redirect('index')
        plano = list(models.Usuario.objects.filter(
            usuario=usuario).values())[0]
        pacote_certo = plano["tipo_plano"]
        if pacote_certo == 0:
            liberar_especifico = "NA"
        elif pacote_certo == 1:
            liberar_especifico = "NP"
        else:
            liberar_especifico = verifica_plano_alimentar(usuario)

        qs = models.MaterialDeApoio.objects.all()
        qs = qs.filter(categoria_do_material__nome__iexact=categoria)
        context = {
            'materiais': qs,
            'cat': categoria,
            'categorias': models.CategoriaMaterialDeApoio.objects.all(),
            'usuario': plano,
            "liberar": liberar_especifico
        }
        return render(self.request, self.template_name, context)

class BuscaMaterialApoio(ListView):
    template_name = "core/material_apoio_busca.html"

    def get(self, *args, **kwargs):
        categoria = self.request.GET.get('categoria', None)
        busca = self.request.GET.get('busca', None)
        usuario = self.request.user.username
        if models.PlanoAlimentar.objects.filter(user=usuario).count() == 0:
            messages.error(self.request, "Você precisa realizar um plano alimentar para ter acesso aos materiais de apoio")
            return redirect('index')
        plano = list(models.Usuario.objects.filter(
            usuario=usuario).values())[0]
        pacote_certo = plano["tipo_plano"]
        if pacote_certo == 0:
            liberar_especifico = "NA"
        elif pacote_certo == 1:
            liberar_especifico = "NP"
        else:
            liberar_especifico = verifica_plano_alimentar(usuario)

        qs = models.MaterialDeApoio.objects.all()
        if categoria != None:
            qs = qs.filter(categoria_do_material__nome__iexact=categoria)
        if busca != None:
            qs = qs.filter(
                Q(palavras_chave_material__icontains=busca) |
                Q(titulo__icontains=busca) |
                Q(texto__icontains=busca) |
                Q(categoria_do_material__palavras_chave__icontains=busca)
            )
        context = {
            'materiais': qs,
            'cat': categoria,
            'busca': busca,
            'categorias': models.CategoriaMaterialDeApoio.objects.all(),
            'usuario': plano,
            "liberar": liberar_especifico
        }
        return render(self.request, self.template_name, context)
    
class TelaCarregamento(TemplateView):
    template_name = "core/tela_espera.html"

    def get(self, *args, **kwargs):
        user = self.request.user.username

        #  Verificando se o usuário preencheu os dados pessoais
        usuario_dados = models.Usuario.objects.filter(usuario=user).values().first()
        if not usuario_dados or usuario_dados.get('dados_pessoais_id') is None:
            messages.add_message(
                self.request, messages.ERROR,
                "É necessário que você responda todas as perguntas com ATENÇÃO, para no final, ter seus Planos Alimentares Personalizados"
            )
            return redirect('/dados_pessoais')

        #  Verificando se o usuário concluiu o cadastro
        dados_pessoais_obj = categorias_models.DadosPessoais.objects.filter(user=user).values().first()
        if not dados_pessoais_obj:
            messages.add_message(self.request, messages.ERROR, "Dados pessoais não encontrados.")
            return redirect('/dados_pessoais')

        sexo = dados_pessoais_obj.get("sexo")
        for k, v in usuario_dados.items():
            if sexo == 'masculino':
                if v is None and k != 'ciclo_menstrual_id':
                    categoria_faltante = str(k).split('_')[0]
                    messages.add_message(
                        self.request, messages.ERROR,
                        f"É necessário que você responda todas as perguntas com ATENÇÃO. Preencha: {categoria_faltante}"
                    )
                    return redirect('/dados_pessoais')
            else:
                if v is None:
                    categoria_faltante = str(k).split('_')[0]
                    messages.add_message(
                        self.request, messages.ERROR,
                        f"É necessário que você responda todas as perguntas com ATENÇÃO. Preencha: {categoria_faltante}"
                    )
                    return redirect('/dados_pessoais')

        # Verificando se o usuário tem avaliações disponíveis
        avaliacoes = usuario_dados.get('avaliacoes', 0)
        if avaliacoes < 1:
            return redirect('/?sem_avaliacao=True')

        #  Verificando tempo restante ou bloqueio
        ver = verifica_usuario(user)
        if not ver:
            messages.add_message(self.request, messages.ERROR, ver)
            return redirect("/?sem_tempo=1")

        #  Coletando dados de todas as categorias
        def get_dict(model):
            obj = model.objects.filter(usuario=user).values().first()
            return dict(obj) if obj else {}

        doencas = get_dict(categorias_models.Doenca)
        medicamentos = get_dict(categorias_models.Medicamento)
        exame_de_sangue = get_dict(categorias_models.ExameSangue)
        intestino = get_dict(categorias_models.Intestino)
        sono = get_dict(categorias_models.Sono)
        cirurgias = get_dict(categorias_models.Cirurgia)
        alcool = get_dict(categorias_models.Alcool)
        suplementos = get_dict(categorias_models.Suplemento)
        dados_antropometricos = get_dict(categorias_models.Antropometricos)
        horarios = get_dict(categorias_models.Horarios)
        exercicios = get_dict(categorias_models.Exercicios)

        ciclo_menstrual = ''
        if sexo != "masculino":
            ciclo_menstrual = get_dict(categorias_models.CicloMenstrual)

        dados_pessoais = dados_pessoais_obj
                # 🔹 Montando o contexto completo
        context = {
            'dados_pessoais': dados_pessoais,
            'doencas': doencas,
            'medicamentos': medicamentos,
            'exame_sangue': exame_de_sangue,
            'intestino': intestino,
            'cirurgias': cirurgias,
            'sono': sono,
            'alcool': alcool,
            'suplementos': suplementos,
            'ciclo_menstrual': ciclo_menstrual,
            'antropometricos': dados_antropometricos,
            'horarios': horarios,
            'exercicios': exercicios,
        }

        return render(self.request, self.template_name, context)

class Evolucao(TemplateView):
    template_name = 'core/tela_evolucao.html'

    def get(self, *args, **kwargs):
        # verificando se o usuario preencheu os dados pessoais
        user = self.request.user.username
        if dict(models.Usuario.objects.filter(usuario=user).values()[0])['dados_pessoais_id'] == None:
            messages.add_message(self.request, messages.ERROR,
                                 "É necessário que você responda todas as perguntas com ATENÇÃO, para no final, ter seus Planos Alimentares Personalizados")
            return redirect('/dados_pessoais')

        # verificando se o usuário concluiu seu cadastro
        sexo = dict(categorias_models.DadosPessoais.objects.filter(
            user=user).values()[0])["sexo"]
        usuario = dict(models.Usuario.objects.filter(usuario=user).values()[0])
        for k, v in usuario.items():
            if sexo == 'masculino':
                if v == None and k != 'ciclo_menstrual_id':
                    categoria_faltante = str(k).split('_')[0]
                    messages.add_message(
                        self.request, messages.ERROR, f"É necessário que você responda todas as perguntas com ATENÇÃO, para no final, ter seus Planos Alimentares Personalizados. Preencha: {categoria_faltante}")
                    return redirect('/dados_pessoais')
            else:
                if v == None:
                    categoria_faltante = str(k).split('_')[0]
                    messages.add_message(
                        self.request, messages.ERROR, f"É necessário que você responda todas as perguntas com ATENÇÃO, para no final, ter seus Planos Alimentares Personalizados. Preencha: {categoria_faltante}")
                    return redirect('/dados_pessoais')
        ver = verifica_usuario(user)
        if not ver:
            messages.add_message(self.request, messages.ERROR,
                                 "Você ultrapassou o limite permitido de dias para o seus Plano.")
            return redirect("/?sem_tempo=1")
        else:
            pass

        # Verificando se o plano do usuário permite user este recurso
        pacote = usuario["tipo_plano"]
        if pacote == 0:
            messages.add_message(self.request, messages.ERROR,
                                 "Você precisa adquirir um plano para acessar os Gráficos de Evolução")
            return redirect("/?sem_tempo=2")
        elif pacote == 1:
            messages.add_message(self.request, messages.ERROR,
                                 "seus Plano não te permite acessar os Gráficos de Evolução")
            return redirect("/?sem_tempo=3")
        # Verificando se o usuário já realizou mais de 1 avaliação
        query = list(models.PlanoAlimentar.objects.filter(
            user=user).order_by("data_realizacao").values())
        if len(query) < 2:
            messages.add_message(self.request, messages.ERROR,
                                 "Você precisa realizar ao menos 2 (duas) avaliações para poder verificar sua evolução.")
            return redirect('index')

        contexto = {
            'pesos': [p["peso"] for p in query],
            'percentual_gordura': [p["percentual_gordura"] for p in query],
            'gordura_corporal': [p["gordura_corporal"] for p in query],
            'cinturas': [p["cintura"] for p in query],
            'abdomen': [p["abdomen"] for p in query],
            'quadril': [p["quadril"] for p in query],
            'datas': [p["data_realizacao"].strftime('%d/%m/%Y') for p in query],

        }
        return render(self.request, self.template_name, contexto)

class Checkout(TemplateView):
    template_name = "core/checkout.html"
class RelatorioEvolucao(TemplateView):
    def get(self, *args, **kwargs):
        # verificando se o usuario preencheu os dados pessoais
        user = self.request.user.username
        if dict(models.Usuario.objects.filter(usuario=user).values()[0])['dados_pessoais_id'] == None:
            messages.add_message(self.request, messages.ERROR,
                                 "É necessário que você responda todas as perguntas com ATENÇÃO, para no final, ter seus Planos Alimentares Personalizados")
            return redirect('/dados_pessoais')

        # verificando se o usuário concluiu seu cadastro
        sexo = dict(categorias_models.DadosPessoais.objects.filter(
            user=user).values()[0])["sexo"]
        usuario = dict(models.Usuario.objects.filter(usuario=user).values()[0])
        for k, v in usuario.items():
            if sexo == 'masculino':
                if v == None and k != 'ciclo_menstrual_id':
                    categoria_faltante = str(k).split('_')[0]
                    messages.add_message(
                        self.request, messages.ERROR, f"É necessário que você responda todas as perguntas com ATENÇÃO, para no final, ter seus Planos Alimentares Personalizados. Preencha: {categoria_faltante}")
                    return redirect('/dados_pessoais')
            else:
                if v == None:
                    categoria_faltante = str(k).split('_')[0]
                    messages.add_message(
                        self.request, messages.ERROR, f"É necessário que você responda todas as perguntas com ATENÇÃO, para no final, ter seus Planos Alimentares Personalizados. Preencha: {categoria_faltante}")
                    return redirect('/dados_pessoais')

        # pegar usuário logado

        ver = verifica_usuario(user)
        if not ver:
            messages.add_message(self.request, messages.ERROR, ver)
            return redirect("/?sem_tempo=1")
        else:
            pass
        # pegar altura do usuario
        dados_pessoais = dict(
            categorias_models.DadosPessoais.objects.filter(user=user).values()[0])
        altura = dados_pessoais["altura"]

        # pegar idade do usuario
        idade = int((datetime.now().date() -
                    dados_pessoais['nascimento']).days // 365.25)

        # pegar sexo do usuario
        sexo = dados_pessoais['sexo']

        # pegar peso do usuario
        dados_antropometricos = dict(categorias_models.Antropometricos.objects.filter(usuario=user).values()[0])
        peso = dados_antropometricos["peso"]

        # pegar percentual de gordura inicial do individuo
        if not models.PlanoAlimentar.objects.filter(user=user).exists():
            messages.add_message(self.request, messages.ERROR, "Realize uma avaliação para ter acesso ao seu relatório de evolução")
            return redirect("/")
        plano = dict(models.PlanoAlimentar.objects.filter(user=user).values().order_by("data_realizacao")[0])

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
        altura_str = str(round(altura/100, 2))
        constante = rel_alt_const[altura_str]

        # calcular peso_ideal (constante * altura**2)
        peso_ideal = round(float(constante) * float((altura/100)**2), 2)
        if peso < peso_ideal -1:
            estado_peso = "abaixo"
        elif peso > peso_ideal + 1:
            estado_peso = "acima"
        else:
            estado_peso = 'na_media'
        # calcular massa_magra_ideal (peso_ideal - (peso_ideal * percentual_gordura_ideal))
        MM_ideal = round(peso_ideal - ((peso_ideal / 100) *percentual_gordura_ideal), 2)
        
        # calcular massa_magra_real (peso - (peso * percentual_gordura_atual))
        MM_real = round(peso - ((peso / 100)*percentual_gordura_atual), 2)
        if MM_real > MM_ideal:
            massa_magra = "acima"
        elif MM_real < MM_ideal:
            massa_magra = "baixa"
        else:
            massa_magra = "normal"


        per_gordura, estado_per_gordura = gera_estado_e_per_gordura(percentual_gordura_atual, idade, sexo)
        if per_gordura == "Valor inválido":
            messages.add_message(self.request, messages.ERROR, "Seu valor de Gordura é inválido, por favor, verifique se você preencheu corretamente o formulário de Antropometria.")
            return redirect("/")

        # pegando ultimos planos alimentares
        planos = list(models.PlanoAlimentar.objects.filter(user=user).values().order_by("data_realizacao"))[0:1]
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
            riscos_quadril.append(calcula_quadril(
                sexo, float(quadril), float(altura)))

        # criando valores de risco abdomen
        riscos_abdomen = []
        for i, abdomen in enumerate(abdomens):
            riscos_abdomen.append(calcula_abdomen(sexo, abdomen))

        # criando valores de risco quadril cintura
        riscos_quad_cint = []
        for i, cintura in enumerate(cinturas):
            riscos_quad_cint.append(cintura_quadril(
                sexo, idade, quadris[i], cinturas[i]))

        # pegando o PESO AJUSTADO
        dados_pessoais = dict(
            categorias_models.DadosPessoais.objects.filter(user=user).values()[0])
        # atribuindo a um dicionário "infos" os dados do usuário pertinentes à fórmula
        dados_antropometricos = dict(categorias_models.Antropometricos.objects.filter(usuario=user).values()[0])
        infos = {
            'idade': int((datetime.now().date() - dados_pessoais['nascimento']).days // 365.25),
            'sexo': dados_pessoais['sexo'],
            'altura': float(dados_pessoais['altura']),
            'abdomen': float(dados_antropometricos['abdomen']),
            'pulso': float(dados_antropometricos['pulso']),
            'peso': float(dados_antropometricos['peso']),
            'quadril': float(dados_antropometricos['quadril'])
        }

        parte = parte_a(infos['peso'], infos['abdomen'], infos['pulso'],
                        infos['sexo'], infos['quadril'], infos['altura'])
        gi = gordura_ideal(infos["sexo"], infos['idade'])
        parte = parte_a(infos['peso'], infos['abdomen'], infos['pulso'],
                        infos['sexo'], infos['quadril'], infos['altura'])

        ga = gordura_atual(infos['peso'], parte, infos['sexo'])
        gi = gordura_ideal(infos["sexo"], infos['idade'])
        gm = gordura_meta(gi, ga, infos["sexo"])
        pa = peso_ajustado(float(infos['peso']), float(ga), float(gm))

        # pegando primeiro plano alimentar
        plano_1 = list(models.PlanoAlimentar.objects.filter(user=user).values().order_by("data_realizacao"))[0]
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
        pa = peso_ajustado(float(infos['peso']), float(percentual_gordura_atual), float(gm))

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
        P9 = P7/100*P8
        R9 = percentual_gordura_ideal
        R10 = 100-R9
        P10 = P7-P9
        S10 = P10
        S9 = R9*S10/R10
        peso_desejado = S9 + S10
        context = {
            "nome_pessoa": usuario["nome"],
            "sobrenome_pessoa": usuario["sobrenome"],
            "peso": peso,
            "estado_peso": estado_peso,
            "massa_media": massa_magra,
            "per_gordura": per_gordura,
            "altura": round(altura/100, 2),
            "sexo": sexo,
            "peso_ideal": round(peso_desejado, 1),
            "peso_ideal_min": int(peso_ideal) - 1,
            "peso_ideal_max": int(peso_ideal) + 1,
            "percentual_gordura_ideal": round(percentual_gordura_ideal, 1),
            'percentual_gordura_real': round(percentual_gordura_atual, 1),
            "estado_per_gordura": estado_per_gordura,
            "peso_real_gordura": round(float(peso) - float(MM_real), 1),
            "peso_ideal_gordura": round(float(percentual_gordura_ideal) * float(MM_real)/float(100 - float(percentual_gordura_ideal)), 1),
            "peso_real_MM": round(MM_real, 1),
            "riscos_cintura": riscos_cintura,
            "riscos_quad_cint": riscos_quad_cint,
            "riscos_abdomen": riscos_abdomen,
            "riscos_quadril": riscos_quadril,
            "kcal_1": int(round((pa*30)/100)*100),
            "kcal_2": int(plano["kcal"]),
            "kcal_3": int(plano["kcal_simples"]),
            "lista": lista_metas,
            "lista_oks": lista_oks
        }
        import pprint
        pprint.pprint(context)

        if sexo == "masculino":
            self.template_name = "core/relatorio_m.html"
            user = self.request.user.username
            passaram_7_dias = verifica_plano_alimentar(user)
            if not passaram_7_dias:
                self.template_name = "core/relatorio_m_incompleto.html"
        else:
            self.template_name = "core/relatorio_evolucao.html"
            user = self.request.user.username
            passaram_7_dias = verifica_plano_alimentar(user)
            if not passaram_7_dias:
                self.template_name = "core/relatorio_f_incompleto.html"
        return render(self.request, self.template_name, context)


class EvolucaoFinal(TemplateView):
    template_name = 'core/evolucao_modelo.html'

    def get(self, *args, **kwargs):

        # verificando se o usuario preencheu os dados pessoais
        user = self.request.user.username
        if not categorias_models.DadosPessoais.objects.filter(usuario=user).exists():
            messages.add_message(self.request, messages.ERROR,
                                 "É necessário que você responda todas as perguntas com ATENÇÃO, para no final, ter seus Planos Alimentares Personalizados")
            return redirect('/dados_pessoais')

        # verificando se o usuário concluiu seu cadastro
        sexo = dict(categorias_models.DadosPessoais.objects.filter(
            user=user).values()[0])["sexo"]
        altura = dict(categorias_models.DadosPessoais.objects.filter(
            user=user).values()[0])["altura"]
        idade = int((datetime.now().date() - dict(categorias_models.DadosPessoais.objects.filter(
            user=user).values()[0])["nascimento"]).days // 365.25)
        usuario = dict(models.Usuario.objects.filter(usuario=user).values()[0])
        for k, v in usuario.items():
            if sexo == 'masculino':
                if v == None and k != 'ciclo_menstrual_id':
                    categoria_faltante = str(k).split('_')[0]
                    messages.add_message(
                        self.request, messages.ERROR, f"É necessário que você responda todas as perguntas com ATENÇÃO, para no final, ter seus Planos Alimentares Personalizados. Preencha: {categoria_faltante}")
                    return redirect('/dados_pessoais')
            else:
                if v == None:
                    categoria_faltante = str(k).split('_')[0]
                    messages.add_message(
                        self.request, messages.ERROR, f"É necessário que você responda todas as perguntas com ATENÇÃO, para no final, ter seus Planos Alimentares Personalizados. Preencha: {categoria_faltante}")
                    return redirect('/dados_pessoais')

        ver = verifica_usuario(user)
        if not ver:
            messages.add_message(self.request, messages.ERROR, ver)
            return redirect("index")
        else:
            pass

        usuario = dict(models.Usuario.objects.filter(usuario=user).values()[0])
        planos = list(models.PlanoAlimentar.objects.filter(user=user).values().order_by("data_realizacao"))[:6]
        
        #verificando se o usuário possui menos de dois planos alimentares realizados
        if len(planos) < 2:
            messages.error(self.request, "Você precisa ter realizado ao menos dois Planos Alimentares para ter acesso à Evolução Alimentar")
            return redirect("index")
        datas_lista = [plano['data_realizacao'].strftime('%d/%m/%Y') for plano in planos]
        datas_planos = {}
        for i in range(len(datas_lista)):
            datas_planos[f'data_{i+1}'] = datas_lista[i]

            
        consultas = {}
        riscos = {}
        i = 1
        for plano in planos:
            ### Consultas ###
            consultas[f'peso_{i}'] = round(plano['peso'], 2 if len(
                str(plano['peso']).split('.')[0]) < 3 else 1)
            consultas[f'per_gordura_{i}'] = round(
                plano['percentual_gordura'], 1)
            consultas[f'massa_magra_{i}'] = round(
                float(plano['peso']) - float(plano['gordura_corporal']), 1)
            consultas[f'peso_gordura_{i}'] = round(plano['gordura_corporal'], 2 if len(
                str(plano['gordura_corporal']).split('.')[0]) < 2 else 1)
            consultas[f'cintura_{i}'] = round(plano['cintura'], 2 if len(
                str(plano['cintura']).split('.')[0]) < 3 else 1)
            consultas[f'abdomen_{i}'] = round(plano['abdomen'], 2 if len(
                str(plano['abdomen']).split('.')[0]) < 3 else 1)
            consultas[f'quadril_{i}'] = round(plano['quadril'], 2 if len(
                str(plano['quadril']).split('.')[0]) < 3 else 1)

            ### Riscos ###
            riscos[f'quadril_{i}'] = calcula_quadril(
                sexo, float(plano['quadril']), float(altura))
            riscos[f'cintura_{i}'] = calcula_cintura(altura, plano['cintura'])
            riscos[f'abdomen_{i}'] = calcula_abdomen(sexo, plano['abdomen'])
            riscos[f'cintura_quadril_{i}'] = cintura_quadril(
                sexo, idade, float(plano['quadril']), float(plano['cintura']))

            i += 1

        # Pegando Kcal
        ultimo_plano = planos[-1]
        print(ultimo_plano)

        # Comparação 2 últimos planos
        ultimos = planos[-2:]
        datas = {}
        i = 1
        for plano in ultimos:
            datas[f'data_{i}'] = plano['data_realizacao'].strftime('%d/%m/%Y')
            i += 1

        kcals = {}
        # pegando os valores caloricos
        parte = parte_a(planos[-1]['peso'], planos[-1]['abdomen'],
                        planos[-1]['pulso'], sexo, planos[-1]['quadril'], altura)
        gi = gordura_ideal(sexo, idade)
        per_gordura_atual = round(float(planos[-1]['percentual_gordura']), 2 if len(str(planos[-2]['percentual_gordura']).split('.')[0]) < 2 else 1)
        gm = gordura_meta(gi, per_gordura_atual, sexo)
        pa = peso_ajustado(float(planos[-1]['peso']), float(per_gordura_atual), float(gm))
        kcals['kcal_1'] = int(round((pa*30)/100)*100)
        kcals['kcal_2'] = int(planos[-1]['kcal'])
        mes_realizacao = int(planos[-1]['data_realizacao'].strftime('%m'))
        meses = {
            1: 'JANEIRO',
            2: 'FEVEREIRO',
            3: 'MARÇO',
            4: 'ABRIL',
            5: 'MAIO',
            6: 'JUNHO',
            7: 'JULHO',
            8: 'AGOSTO',
            9: 'SETEMBRO',
            10: 'OUTUBRO',
            11: 'NOVEMBRO',
            12: 'DEZEMBRO',
        }
        kcals['mes'] = meses[mes_realizacao]
        # Pegando as diferenças
        diferencas = {}

        # diferenca de peso
        diferenca_peso = float(planos[-1]['peso']) - float(planos[-2]['peso'])
        diferenca_peso = round(diferenca_peso, 2 if len(str(diferenca_peso).split('.')[0]) < 2 else 1)
        if diferenca_peso == 0:
            diferenca_peso_estado = 'MANUTENCAO'
        elif 0 < diferenca_peso <= 1.5:
            diferenca_peso_estado = 'AUMENTO'
        elif diferenca_peso > 1.5:
            diferenca_peso_estado = 'GRANDE AUMENTO'
        elif -1.5 <= diferenca_peso < 0:
            diferenca_peso_estado = 'DIMINUICAO'
        elif diferenca_peso < -1.5:
            diferenca_peso_estado = 'GRANDE DIMINUICAO'
        diferenca_peso = str(abs(diferenca_peso))
        diferencas['peso'] = diferenca_peso
        diferencas['peso_descricao'] = diferenca_peso_estado

        # diferenca de % gordura
        diferenca_percentual_gordura = float(planos[-1]['percentual_gordura']) - float(planos[-2]['percentual_gordura'])
        diferenca_percentual_gordura = round(diferenca_percentual_gordura, 2 if len(str(diferenca_percentual_gordura).split('.')[0]) < 2 else 1)
        if diferenca_percentual_gordura == 0:
            diferenca_percentual_gordura_estado = 'MANUTENCAO'
        elif 0 < diferenca_percentual_gordura <= 0.2:
            diferenca_percentual_gordura_estado = 'LEVE AUMENTO'
        elif diferenca_percentual_gordura > 0.2:
            diferenca_percentual_gordura_estado = 'AUMENTO'
        elif -0.2 <= diferenca_percentual_gordura < 0:
            diferenca_percentual_gordura_estado = 'LEVE DIMINUICAO'
        elif diferenca_percentual_gordura < -0.2:
            diferenca_percentual_gordura_estado = 'DIMINUICAO'
        diferenca_percentual_gordura = str(abs(diferenca_percentual_gordura))
        diferencas['percentual_gordura'] = diferenca_percentual_gordura
        diferencas['percentual_gordura_descricao'] = diferenca_percentual_gordura_estado

        # diferenca de peso da gordura
        diferenca_peso_gordura = float(
            planos[-1]['gordura_corporal']) - float(planos[-2]['gordura_corporal'])
        diferenca_peso_gordura = round(diferenca_peso_gordura, 2 if len(
            str(diferenca_peso_gordura).split('.')[0]) < 2 else 1)
        if diferenca_peso_gordura == 0:
            diferenca_peso_gordura_estado = 'MANUTENCAO'
        elif diferenca_peso_gordura > 0:
            diferenca_peso_gordura_estado = 'AUMENTO'
        elif -0.2 <= diferenca_peso_gordura < 0:
            diferenca_peso_gordura_estado = 'LEVE DIMINUICAO'
        elif diferenca_peso_gordura < -0.2:
            diferenca_peso_gordura_estado = 'DIMINUICAO'
        diferenca_peso_gordura = str(abs(diferenca_peso_gordura)) 
        diferencas['peso_gordura'] = diferenca_peso_gordura
        diferencas['peso_gordura_descricao'] = diferenca_peso_gordura_estado

        # diferenca de Massa Magra
        diferenca_MM = (float(planos[-1]['peso']) - float(planos[-1]['gordura_corporal'])) - (
            float(planos[-2]['peso']) - float(planos[-2]['gordura_corporal']))
        diferenca_MM = round(diferenca_MM, 2 if len(
            str(diferenca_MM).split('.')[0]) < 2 else 1)
        if diferenca_MM == 0:
            diferenca_MM_estado = 'MANUTENCAO'
        elif 0 < diferenca_MM <= 0.2:
            diferenca_MM_estado = 'LEVE AUMENTO'
        elif diferenca_MM > 0.2:
            diferenca_MM_estado = 'AUMENTO'
        elif diferenca_MM < 0:
            diferenca_MM_estado = 'DIMINUICAO'
        diferenca_MM = str(abs(diferenca_MM))
        diferencas['peso_MM'] = diferenca_MM
        diferencas['peso_MM_descricao'] = diferenca_MM_estado

        # Pegando a meta de evolução
        per_gordura_inicial = round(float(planos[0]['percentual_gordura']), 2 if len(str(planos[0]['percentual_gordura']).split('.')[0]) < 2 else 1)
        per_gordura_meta = gm

        valores = {
            'meta_1': per_gordura_inicial,
            'meta_1_estado': 'OK'
        }
        i = 2
        for _ in range(65):
            if per_gordura_inicial >= per_gordura_meta:
                per_gordura_inicial -= 0.3
                valores[f'meta_{i}'] = round(per_gordura_inicial, 2 if len(
                    str(per_gordura_inicial).split('.')[0]) < 2 else 1)
                if per_gordura_atual <= per_gordura_inicial:
                    valores[f'meta_{i}_estado'] = 'OK'
                else:
                    valores[f'meta_{i}_estado'] = '__'
            else:
                valores[f'meta_{i}'] = '____'
                valores[f'meta_{i}_estado'] = '__'
            i += 1

        context = {
            "nome_pessoa": usuario["nome"],
            "sobrenome_pessoa": usuario["sobrenome"],
            'datas_planos': datas_planos,
            'consultas': consultas,
            'riscos': riscos,
            'datas': datas,
            'diferencas': diferencas,
            'valores': valores,
            'kcals': kcals
        }
        import pprint

        # justo antes del return
        pprint.pprint(context)
        return render(self.request, self.template_name, context)

class Calculadora(TemplateView):
    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            usuario = self.request.user.username
            if not list(models.Usuario.objects.filter(usuario=usuario).values()):
                messages.add_message(
                    self.request, messages.ERROR, "Usuário não encontrado")
                return redirect('login')

            usuario = list(models.Usuario.objects.filter(
                usuario=usuario).values())[0]
            context = {
                'usuario': usuario,
                'sem_avaliacao': self.request.GET.get('sem_avaliacao')
            }
        else:
            redirect("login")
        return render(self.request, 'core/calculadora.html', context)

    def post(self, *args, **kwargs):
        usuario = self.request.user.username
        usuario = list(models.Usuario.objects.filter(
            usuario=usuario).values())[0]

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
        MM_real = round(peso - (peso * ga/100), 1)
        # pegar gordura ideal
        gordura_i = gordura_ideal(sexo, idade)

        fator_multiplicação = 1 + gordura_i/100
        peso_ideal = round(MM_real * fator_multiplicação, 1)
        peso_gordura_ideal = round(peso_ideal - MM_real, 1)

        # gordura e peso perfeitos
        gordura_p = gordura_perfeita(sexo, idade)
        fator_multiplicação = 1 + gordura_p/100
        peso_perfeito = round(MM_real * fator_multiplicação, 1)
        peso_gordura_perfeita = round(peso_perfeito - MM_real, 1)

        context = {
            'usuario': usuario,
            'sem_avaliacao': self.request.GET.get('sem_avaliacao'),
            "percentual_gordura_atual": ga,
            "peso_atual": peso,
            "peso_ideal": peso_ideal,
            "peso_perfeito": peso_perfeito,
            "MM_real": MM_real,
            "peso_gordura_real": round(peso - MM_real, 1),
            "peso_gordura_ideal": round((gordura_i*MM_real)/(100-gordura_i), 1),
            "peso_gordura_perfeita": round((gordura_p*MM_real)/(100-gordura_p), 1),
            "gordura_ideal": gordura_i,
            "gordura_perfeita": gordura_p,
            "perder_bom": round(round(peso - MM_real, 1) - round((gordura_i*MM_real)/(100-gordura_i), 1), 2),
            "perder_perfeito": round(round(peso - MM_real, 1) - round((gordura_p*MM_real)/(100-gordura_p), 1), 2)
        }
        from pprint import pprint
        pprint(context)

        return render(self.request, 'core/calculadora.html', context)

class TermosCondicoes(TemplateView):
    template_name = "core/termos_e_condicoes.html"

    def get(self, *args, **kwargs):
        modelo = list(models.Termos.objects.filter().values())
        if len(modelo) != 0:
            modelo = modelo[0]
        context = {
            "termo": modelo,
            "is_termos": True
        }
        return render(self.request, self.template_name, context)

class RecuperarSenha(TemplateView):
    template_name = 'core/recuperar_senha.html'

    def post(self, *args, **kwargs):
        email = self.request.POST.get('email')
        user = list(models.Usuario.objects.filter(email=email).values())
        if user != []:
            # Enviando Mensagem para o primeiro Colocado
            login = user[0]['usuario']
            senha = user[0]['senha']
            subject, from_email, to = 'Recuperação de Senha', 'nao-responda@emagrecimentodefinitivo.app.br', user[
                0]['email']
            text_content = 'Recuperação de Senha'
            html_content = (f'''
            <h1>Uma recuperação de senha foi solicitada!</h1>
            <h2>Caso não tenha sido você que solicitou, por favor entre em contato comigo o mais rápido possível!</h2>
            <h3>Suas informações: </h3>
            <p></p>
            <h2>Login: <strong>{login}</strong></h2>
            <h2>Senha: <strong>{senha}</strong></h2>

            Att: Israel Adolfo | Nutricionista Esportivo
            ''')
            msg = EmailMultiAlternatives(
                subject, text_content, from_email, [to])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
        academia = list(models.Academia.objects.filter(email=email).values())
        if academia != []:
            # Enviando Mensagem para o primeiro Colocado
            login = academia[0]['cnpj']
            senha = academia[0]['senha']
            subject, from_email, to = 'Recuperação de Senha', 'nao-responda@emagrecimentodefinitivo.app.br', user[
                0]['email']
            text_content = 'Recuperação de Senha'
            html_content = (f'''
            <h1>Uma recuperação de senha foi solicitada!</h1>
            <h2>Caso não tenha sido você que solicitou, por favor entre em contato comigo o mais rápido possível!</h2>
            <h3>Suas informações: </h3>
            <p></p>
            <h2>Login: <strong>{login}</strong></h2>
            <h2>Senha: <strong>{senha}</strong></h2>

            Att: Israel Adolfo | Nutricionista Esportivo
            ''')
            msg = EmailMultiAlternatives(
                subject, text_content, from_email, [to])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
        messages.add_message(self.request, messages.SUCCESS,
                             'Se o email informado estiver entre os cadastros no sistema será enviada uma mensagem contendo suas informações de login e senha!')
        return redirect('recuperar_senha')

class ExcluirUsuario(TemplateView):
    template_name = "core/z_excluir_usuario.html"
    def get(self, *args, **kwargs):
        if self.request.user.is_staff:
            return render(self.request, self.template_name)
        else:
            return redirect('/')
    def post(self, *args, **kwargs):
        if self.request.user.is_staff:
            req = self.request.POST
            if str(req.get('confirmacao')) == 'confirmar':
                user = req.get('user')
                models.Usuario.objects.filter(usuario=user).delete()
                categorias_models.DadosPessoais.objects.filter(user=user).delete()
                User.objects.filter(username=user).delete()
                categorias_models.Doenca.objects.filter(user=user).delete()
                categorias_models.Medicamento.objects.filter(user=user).delete()
                categorias_models.Cirurgia.objects.filter(user=user).delete()
                categorias_models.ExameSangue.objects.filter(user=user).delete()
                categorias_models.Intestino.objects.filter(user=user).delete()
                categorias_models.Sono.objects.filter(user=user).delete()
                categorias_models.Alcool.objects.filter(user=user).delete()
                categorias_models.CicloMenstrual.objects.filter(user=user).delete()
                categorias_models.Antropometricos.objects.filter(user=user).delete()
                categorias_models.Horarios.objects.filter(user=user).delete()
                categorias_models.Exercicios.objects.filter(user=user).delete()
                messages.success(self.request, f"Usuário {user} excluído com sucesso")
            else:
                messages.error(self.request, "Você não digitou 'confirmar' então o usuário não foi excluido")
            return render(self.request, self.template_name)
        else:
            return redirect('/')

class MateriaisUsuario(TemplateView):
    template_name = "core/materiais_usuario.html"

    def get(self, *args, **kwargs):
        return render(self.request, self.template_name)
        
def salvar_imagem(request):
    if request.method == 'POST':
        #transformando o base64 em imagem
        imagem64 = request.POST.get('imagem')
        #pegando imagem em string e convertendo para bytes
        imagem64 = imagem64.split(',')[1]
        imagem64 = imagem64.encode()
        imagem64 = base64.b64decode(imagem64)
        imagem64 = io.BytesIO(imagem64)
        

        #transformando data para date
        data_realizacao = request.POST.get('data_realizacao')
        data_realizacao = datetime.strptime(data_realizacao, '%Y-%m-%d').date()

        #pegando username
        user = request.POST.get('username')

        #pegando o tipo de plano
        categoria = request.POST.get('tipo_plano')
        
        #convertendo a imagem para ImageFile
        imagem = ImageFile(imagem64, name=f'{user}_{data_realizacao}_plano_alimentar_{categoria}.png')

        #procurando na tabela de MaterialdeClientes se já existe um registro com o mesmo username e categoria,
        #ordenado por data de realização mais recente
        material = models.MaterialdeClientes.objects.filter(usuario=user, categoria=categoria).order_by('-data_criacao')
        
        #se não existir nenhum registro, então é criado um novo
        if not material.exists():
            form = models.MaterialdeClientes(usuario=user, categoria=categoria, data_criacao=data_realizacao, material=imagem)
            form.save()
        else:

            #se já existe registros, verifica se existem 6 registros, se existir, exclui o mais antigo
            if material.count() == 6:
                material[5].delete()
            #pegando o material mais recente
            material = material[0]
            #verificando se a data de realização é a mesma do registro mais recente
            if material.data_criacao == data_realizacao:
                pass
            else:
                #cria um novo registro
                form = models.MaterialdeClientes(usuario=user, categoria=categoria, data_criacao=data_realizacao, material=imagem)
                form.save()

    return HttpResponse("ok")


@login_required
def gerar_pdf(request):
    tipo = request.GET.get("tipo")
    user = request.user.username  # asumimos que el user está logueado

    if tipo == "com_treino":
        # ---- reutilizamos la lógica de ExibeAvaliacaoTreino ----
        avaliacao_mais_recente = list(
            models.PlanoAlimentar.objects.filter(user=user).values()
        )[-1]

        usuario_obj = models.Usuario.objects.get(usuario=user)

        data_realizacao = avaliacao_mais_recente["data_realizacao"]
        data_formatada = data_realizacao.strftime("%d/%m/%Y")

        treino_cedo = False
        if avaliacao_mais_recente['horario_treino'] < avaliacao_mais_recente['café_da_manha']:
            treino_cedo = True

        context = {
            'nome_completo': f"{usuario_obj.nome} {usuario_obj.sobrenome}",
            'treino': 's',
            'treino_cedo': treino_cedo,
            'kcal': avaliacao_mais_recente['kcal'],
            'cafe_da_manha': avaliacao_mais_recente['café_da_manha'],
            'almoco': avaliacao_mais_recente['almoco'],
            'lanche_1': avaliacao_mais_recente['lanche_1'],
            'lanche_2': avaliacao_mais_recente['lanche_2'],
            'lanche_3': avaliacao_mais_recente['lanche_3'],
            'jantar': avaliacao_mais_recente['horario_janta'],
            "data_realizacao": data_formatada,
            "username": user,
            "tipo_plano": "avaliacao_com_treino",
        }

    elif tipo == "sem_treino":
        avaliacao_mais_recente = list(
            models.PlanoAlimentar.objects.filter(user=user).values()
        )[-1]

        usuario_obj = models.Usuario.objects.get(usuario=user)

        data_realizacao = avaliacao_mais_recente["data_realizacao"]
        data_formatada = data_realizacao.strftime("%d/%m/%Y")

        context = {
            'nome_completo': f"{usuario_obj.nome} {usuario_obj.sobrenome}",
            'treino': 'n',
            'treino_cedo': False,
            'kcal': avaliacao_mais_recente['kcal_simples'],
            'cafe_da_manha': avaliacao_mais_recente['café_da_manha'],
            'almoco': avaliacao_mais_recente['almoco'],
            'lanche_1': avaliacao_mais_recente['lanche_1'],
            'lanche_2': avaliacao_mais_recente['lanche_2'],
            'lanche_3': avaliacao_mais_recente['lanche_3'],
            "data_realizacao": data_formatada,
            "username": user,
            "tipo_plano": "avaliacao_sem_treino",
        }

    else:
        return HttpResponse("Tipo inválido", status=400)

    # ---- generar HTML ----
    html_string = render_to_string("core/pdf_template.html", context)

    # ---- generar PDF ----
    with tempfile.NamedTemporaryFile(delete=False) as output:
        HTML(string=html_string, base_url=request.build_absolute_uri('/')).write_pdf(
            output.name,
            stylesheets=[CSS(string="""
                @page {
                    size: 240mm 1300mm;   /* una sola hoja larga */
                    margin: 10mm 10mm 15mm 10mm;
                }

                html, body {
                    margin: 0;
                    padding: 0;
                    font-family: 'Open Sans', sans-serif;
                    font-size: 12pt;
                    line-height: 1.4;
                    background: white;
                }

                .card-refeicao {
                    border: 1px solid #ddd;
                    border-radius: 8px;
                    padding: 10px 15px;
                    margin-bottom: 8px;
                    page-break-inside: avoid;
                }

                * {
                    page-break-before: avoid;
                    page-break-after: avoid;
                    page-break-inside: avoid;
                }

            """)]

        )
        output.seek(0)
        pdf = output.read()

    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="plano_alimentar.pdf"'
    return response



# === Logging para debug controlado ===
logger = logging.getLogger(__name__)
class CapaRelatorioView(TemplateView):    
    template_name = 'core/relatorio_pdf_femenino.html'
    def get(self, *args, **kwargs):
        # verificando se o usuario preencheu os dados pessoais
        user = self.request.user.username
        if not categorias_models.DadosPessoais.objects.filter(usuario=user).exists():
            messages.add_message(self.request, messages.ERROR,
                                 "É necessário que você responda todas as perguntas com ATENÇÃO, para no final, ter seus Planos Alimentares Personalizados")
            return redirect('/dados_pessoais')

        # verificando se o usuário concluiu seu cadastro
        sexo = dict(categorias_models.DadosPessoais.objects.filter(
            user=user).values()[0])["sexo"]
        altura = dict(categorias_models.DadosPessoais.objects.filter(
            user=user).values()[0])["altura"]
        idade = int((datetime.now().date() - dict(categorias_models.DadosPessoais.objects.filter(
            user=user).values()[0])["nascimento"]).days // 365.25)
        usuario = dict(models.Usuario.objects.filter(usuario=user).values()[0])

        if sexo in ("m", "masculino"):
            self.template_name = "core/relatorio_pdf_masculino.html"
        elif sexo in ("f", "feminino"):
            self.template_name = "core/relatorio_pdf_femenino.html"
        else:
            messages.error(self.request, "Sexo não identificado. Verifique seu cadastro.")
            return redirect('/dados_pessoais')

        for k, v in usuario.items():
            if sexo == 'masculino':
                if v == None and k != 'ciclo_menstrual_id':
                    categoria_faltante = str(k).split('_')[0]
                    messages.add_message(
                        self.request, messages.ERROR, f"É necessário que você responda todas as perguntas com ATENÇÃO, para no final, ter seus Planos Alimentares Personalizados. Preencha: {categoria_faltante}")
                    return redirect('/dados_pessoais')
            else:
                if v == None:
                    categoria_faltante = str(k).split('_')[0]
                    messages.add_message(
                        self.request, messages.ERROR, f"É necessário que você responda todas as perguntas com ATENÇÃO, para no final, ter seus Planos Alimentares Personalizados. Preencha: {categoria_faltante}")
                    return redirect('/dados_pessoais')

        ver = verifica_usuario(user)
        if not ver:
            messages.add_message(self.request, messages.ERROR, ver)
            return redirect("index")
        else:
            pass

        usuario = dict(models.Usuario.objects.filter(usuario=user).values()[0])
        planos = list(models.PlanoAlimentar.objects.filter(user=user).values().order_by("data_realizacao"))[:6]
        
        #verificando se o usuário possui menos de dois planos alimentares realizados
        if len(planos) < 2:
            messages.error(self.request, "Você precisa ter realizado ao menos dois Planos Alimentares para ter acesso à Evolução Alimentar")
            return redirect("index")
        datas_lista = [plano['data_realizacao'].strftime('%d/%m/%Y') for plano in planos]
        datas_planos = {}
        for i in range(len(datas_lista)):
            datas_planos[f'data_{i+1}'] = datas_lista[i]

            
        consultas = {}
        riscos = {}
        i = 1
        for plano in planos:
            ### Consultas ###
            consultas[f'peso_{i}'] = round(plano['peso'], 2 if len(
                str(plano['peso']).split('.')[0]) < 3 else 1)
            consultas[f'per_gordura_{i}'] = round(
                plano['percentual_gordura'], 1)
            consultas[f'massa_magra_{i}'] = round(
                float(plano['peso']) - float(plano['gordura_corporal']), 1)
            consultas[f'peso_gordura_{i}'] = round(plano['gordura_corporal'], 2 if len(
                str(plano['gordura_corporal']).split('.')[0]) < 2 else 1)
            consultas[f'cintura_{i}'] = round(plano['cintura'], 2 if len(
                str(plano['cintura']).split('.')[0]) < 3 else 1)
            consultas[f'abdomen_{i}'] = round(plano['abdomen'], 2 if len(
                str(plano['abdomen']).split('.')[0]) < 3 else 1)
            consultas[f'quadril_{i}'] = round(plano['quadril'], 2 if len(
                str(plano['quadril']).split('.')[0]) < 3 else 1)

            ### Riscos ###
            riscos[f'quadril_{i}'] = calcula_quadril(
                sexo, float(plano['quadril']), float(altura))
            riscos[f'cintura_{i}'] = calcula_cintura(altura, plano['cintura'])
            riscos[f'abdomen_{i}'] = calcula_abdomen(sexo, plano['abdomen'])
            riscos[f'cintura_quadril_{i}'] = cintura_quadril(
                sexo, idade, float(plano['quadril']), float(plano['cintura']))

            i += 1

        # Pegando Kcal
        ultimo_plano = planos[-1]
        print(ultimo_plano)

        # Comparação 2 últimos planos
        ultimos = planos[-2:]
        datas = {}
        i = 1
        for plano in ultimos:
            datas[f'data_{i}'] = plano['data_realizacao'].strftime('%d/%m/%Y')
            i += 1

        kcals = {}
        # pegando os valores caloricos
        parte = parte_a(planos[-1]['peso'], planos[-1]['abdomen'],
                        planos[-1]['pulso'], sexo, planos[-1]['quadril'], altura)
        gi = gordura_ideal(sexo, idade)
        per_gordura_atual = round(float(planos[-1]['percentual_gordura']), 2 if len(str(planos[-2]['percentual_gordura']).split('.')[0]) < 2 else 1)
        gm = gordura_meta(gi, per_gordura_atual, sexo)
        pa = peso_ajustado(float(planos[-1]['peso']), float(per_gordura_atual), float(gm))
        kcals['kcal_1'] = int(round((pa*30)/100)*100)
        kcals['kcal_2'] = int(planos[-1]['kcal'])
        mes_realizacao = int(planos[-1]['data_realizacao'].strftime('%m'))
        meses = {
            1: 'JANEIRO',
            2: 'FEVEREIRO',
            3: 'MARÇO',
            4: 'ABRIL',
            5: 'MAIO',
            6: 'JUNHO',
            7: 'JULHO',
            8: 'AGOSTO',
            9: 'SETEMBRO',
            10: 'OUTUBRO',
            11: 'NOVEMBRO',
            12: 'DEZEMBRO',
        }
        kcals['mes'] = meses[mes_realizacao]
        # Pegando as diferenças
        diferencas = {}

        # diferenca de peso
        diferenca_peso = float(planos[-1]['peso']) - float(planos[-2]['peso'])
        diferenca_peso = round(diferenca_peso, 2 if len(str(diferenca_peso).split('.')[0]) < 2 else 1)
        if diferenca_peso == 0:
            diferenca_peso_estado = 'MANUTENCAO'
        elif 0 < diferenca_peso <= 1.5:
            diferenca_peso_estado = 'AUMENTO'
        elif diferenca_peso > 1.5:
            diferenca_peso_estado = 'GRANDE AUMENTO'
        elif -1.5 <= diferenca_peso < 0:
            diferenca_peso_estado = 'DIMINUICAO'
        elif diferenca_peso < -1.5:
            diferenca_peso_estado = 'GRANDE DIMINUICAO'
        diferenca_peso = str(abs(diferenca_peso))
        diferencas['peso'] = diferenca_peso
        diferencas['peso_descricao'] = diferenca_peso_estado

        # diferenca de % gordura
        diferenca_percentual_gordura = float(planos[-1]['percentual_gordura']) - float(planos[-2]['percentual_gordura'])
        diferenca_percentual_gordura = round(diferenca_percentual_gordura, 2 if len(str(diferenca_percentual_gordura).split('.')[0]) < 2 else 1)
        if diferenca_percentual_gordura == 0:
            diferenca_percentual_gordura_estado = 'MANUTENCAO'
        elif 0 < diferenca_percentual_gordura <= 0.2:
            diferenca_percentual_gordura_estado = 'LEVE AUMENTO'
        elif diferenca_percentual_gordura > 0.2:
            diferenca_percentual_gordura_estado = 'AUMENTO'
        elif -0.2 <= diferenca_percentual_gordura < 0:
            diferenca_percentual_gordura_estado = 'LEVE DIMINUICAO'
        elif diferenca_percentual_gordura < -0.2:
            diferenca_percentual_gordura_estado = 'DIMINUICAO'
        diferenca_percentual_gordura = str(abs(diferenca_percentual_gordura))
        diferencas['percentual_gordura'] = diferenca_percentual_gordura
        diferencas['percentual_gordura_descricao'] = diferenca_percentual_gordura_estado

        # diferenca de peso da gordura
        diferenca_peso_gordura = float(
            planos[-1]['gordura_corporal']) - float(planos[-2]['gordura_corporal'])
        diferenca_peso_gordura = round(diferenca_peso_gordura, 2 if len(
            str(diferenca_peso_gordura).split('.')[0]) < 2 else 1)
        if diferenca_peso_gordura == 0:
            diferenca_peso_gordura_estado = 'MANUTENCAO'
        elif diferenca_peso_gordura > 0:
            diferenca_peso_gordura_estado = 'AUMENTO'
        elif -0.2 <= diferenca_peso_gordura < 0:
            diferenca_peso_gordura_estado = 'LEVE DIMINUICAO'
        elif diferenca_peso_gordura < -0.2:
            diferenca_peso_gordura_estado = 'DIMINUICAO'
        diferenca_peso_gordura = str(abs(diferenca_peso_gordura)) 
        diferencas['peso_gordura'] = diferenca_peso_gordura
        diferencas['peso_gordura_descricao'] = diferenca_peso_gordura_estado

        # diferenca de Massa Magra
        diferenca_MM = (float(planos[-1]['peso']) - float(planos[-1]['gordura_corporal'])) - (
            float(planos[-2]['peso']) - float(planos[-2]['gordura_corporal']))
        diferenca_MM = round(diferenca_MM, 2 if len(
            str(diferenca_MM).split('.')[0]) < 2 else 1)
        if diferenca_MM == 0:
            diferenca_MM_estado = 'MANUTENCAO'
        elif 0 < diferenca_MM <= 0.2:
            diferenca_MM_estado = 'LEVE AUMENTO'
        elif diferenca_MM > 0.2:
            diferenca_MM_estado = 'AUMENTO'
        elif diferenca_MM < 0:
            diferenca_MM_estado = 'DIMINUICAO'
        diferenca_MM = str(abs(diferenca_MM))
        diferencas['peso_MM'] = diferenca_MM
        diferencas['peso_MM_descricao'] = diferenca_MM_estado

        # Pegando a meta de evolução
        per_gordura_inicial = round(float(planos[0]['percentual_gordura']), 2 if len(str(planos[0]['percentual_gordura']).split('.')[0]) < 2 else 1)
        per_gordura_meta = gm

        valores = {
            'meta_1': per_gordura_inicial,
            'meta_1_estado': 'OK'
        }
        i = 2
        for _ in range(65):
            if per_gordura_inicial >= per_gordura_meta:
                per_gordura_inicial -= 0.3
                valores[f'meta_{i}'] = round(per_gordura_inicial, 2 if len(
                    str(per_gordura_inicial).split('.')[0]) < 2 else 1)
                if per_gordura_atual <= per_gordura_inicial:
                    valores[f'meta_{i}_estado'] = 'OK'
                else:
                    valores[f'meta_{i}_estado'] = '__'
            else:
                valores[f'meta_{i}'] = '____'
                valores[f'meta_{i}_estado'] = '__'
            i += 1

        metas = []
        for i in range(1, 49):  # ajustá el rango según cuántas tengas
            valor = valores.get(f"meta_{i}", "-")
            estado = valores.get(f"meta_{i}_estado", "")
            metas.append({
                "num": i,
                "valor": valor,
                "estado": estado
            })

        # 🔹 Partir la lista metas en dos mitades iguales
        metas_1 = metas[:24]
        metas_2 = metas[24:]

        # 🔹 Emparejar los dos bloques (una fila con dos metas)
        filas_metas = []
        for i in range(len(metas_1)):
            m1 = metas_1[i]
            m2 = metas_2[i] if i < len(metas_2) else None
            filas_metas.append((m1, m2))
        context = {
            "nome_pessoa": usuario["nome"],
            "sobrenome_pessoa": usuario["sobrenome"],
            'datas_planos': datas_planos,
            't': consultas,
            'riscos': riscos,
            'datas': datas,
            'diferencas': diferencas,
            'valores': valores,
            'kcals': kcals,
           'filas_metas': filas_metas,
        }
        
        return self._gerar_pdf(context)
        
    

    def _gerar_pdf(self, context):

        html_string = render_to_string(self.template_name, context)

        # --- CSS ---
        css = CSS(string='''
            @page { size: A4; margin: 20mm; }
            body { font-family: 'Open Sans', sans-serif; font-size: 11pt; color: #333; }
            .RC-item { background: #f7f9fc; border-radius: 8px; padding: 8px 14px; margin-bottom: 6px; }
            .RC-label { font-weight: 600; color: #1e3a8a; }
            .RC-desc { font-size: 10pt; color: #555; margin-left: 6px; }
        ''')

        # --- Generar PDF ---
        start_pdf = time.time()
        with tempfile.NamedTemporaryFile(delete=True) as output:
            HTML(string=html_string, base_url=str(settings.BASE_DIR)).write_pdf(output.name, stylesheets=[css])
            output.seek(0)
            pdf = output.read()

        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="relatorio_capa.pdf"'

        return response

# === Logging para debug controlado (opcional) ===
logger = logging.getLogger(__name__)

class RelatorioEvolucaoNew(TemplateView):

    # No fijamos template por defecto porque lo definimos según sexo más abajo
    template_name = None

    def get(self, *args, **kwargs):
        # verificando se o usuario preencheu os dados pessoais
        user = self.request.user.username
        idade = user[1]
        

        if dict(models.Usuario.objects.filter(usuario=user).values()[0])['dados_pessoais_id'] is None:
            messages.add_message(self.request, messages.ERROR,
                                 "É necessário que você responda todas as perguntas com ATENÇÃO, para no final, ter seus Planos Alimentares Personalizados")
            return redirect('/dados_pessoais')

        # verificando se o usuário concluiu seu cadastro
        sexo = dict(categorias_models.DadosPessoais.objects.filter(
            user=user).values()[0])["sexo"]
        usuario = dict(models.Usuario.objects.filter(usuario=user).values()[0])

        for k, v in usuario.items():
            if sexo == 'masculino':
                if v is None and k != 'ciclo_menstrual_id':
                    categoria_faltante = str(k).split('_')[0]
                    messages.add_message(
                        self.request, messages.ERROR,
                        f"É necessário que você responda todas as perguntas com ATENÇÃO, para no final, ter seus Planos Alimentares Personalizados. Preencha: {categoria_faltante}"
                    )
                    return redirect('/dados_pessoais')
            else:
                if v is None:
                    categoria_faltante = str(k).split('_')[0]
                    messages.add_message(
                        self.request, messages.ERROR,
                        f"É necessário que você responda todas as perguntas com ATENÇÃO, para no final, ter seus Planos Alimentares Personalizados. Preencha: {categoria_faltante}"
                    )
                    return redirect('/dados_pessoais')

        # pegar usuário logado
        ver = verifica_usuario(user)
        if not ver:
            messages.add_message(self.request, messages.ERROR, ver)
            return redirect("/?sem_tempo=1")

        # pegar altura do usuario
        dados_pessoais = dict(
            categorias_models.DadosPessoais.objects.filter(user=user).values()[0])
        altura = dados_pessoais["altura"]

        # pegar idade do usuario
        idade = int((datetime.now().date() - dados_pessoais['nascimento']).days // 365.25)

        # pegar sexo do usuario (refresca)
        sexo = dados_pessoais['sexo']

        # pegar peso do usuario
        dados_antropometricos = dict(
            categorias_models.Antropometricos.objects.filter(usuario=user).values()[0])
        peso = dados_antropometricos["peso"]

        # pegar percentual de gordura inicial do individuo
        if not models.PlanoAlimentar.objects.filter(user=user).exists():
            messages.add_message(self.request, messages.ERROR, "Realize uma avaliação para ter acesso ao seu relatório de evolução")
            return redirect("/")
        plano = dict(models.PlanoAlimentar.objects.filter(user=user).values().order_by("data_realizacao")[0])

        percentual_gordura_atual = plano["percentual_gordura"]

        # pegar percentual ideal de gordura para idade e sexo
        percentual_gordura_ideal = gordura_ideal(sexo, idade)

        # criar valores das constantes para multiplicar pela altura
        i_altura = 1.45
        i_const = 19.5
        rel_alt_const = dict()
        for _ in range(100):
            rel_alt_const[f"{i_altura:.2f}"] = round(i_const, 1)
            i_altura = i_altura + 0.01
            i_const += 0.1

        # pegar o valor da constante que corresponde à altura do usuário
        altura_str = str(round(altura/100, 2))
        constante = rel_alt_const[altura_str]

        # calcular peso_ideal (constante * altura**2)
        peso_ideal = round(float(constante) * float((altura/100)**2), 2)
        if peso < peso_ideal - 1:
            estado_peso = "abaixo"
        elif peso > peso_ideal + 1:
            estado_peso = "acima"
        else:
            estado_peso = 'na_media'

        # calcular massa magra ideal e real
        MM_ideal = round(peso_ideal - ((peso_ideal / 100) * percentual_gordura_ideal), 2)
        MM_real = round(peso - ((peso / 100) * percentual_gordura_atual), 2)
        if MM_real > MM_ideal:
            massa_magra = "acima"
        elif MM_real < MM_ideal:
            massa_magra = "baixa"
        else:
            massa_magra = "normal"

        per_gordura, estado_per_gordura = gera_estado_e_per_gordura(percentual_gordura_atual, idade, sexo)
        if per_gordura == "Valor inválido":
            messages.add_message(self.request, messages.ERROR,
                                 "Seu valor de Gordura é inválido, por favor, verifique se você preencheu corretamente o formulário de Antropometria.")
            return redirect("/")

        # pegar último(s) planos alimentares (mantém tua lógica)
        planos = list(models.PlanoAlimentar.objects.filter(user=user).values().order_by("data_realizacao"))[0:1]
        quadris, cinturas, abdomens = [], [], []
        for p in planos:
            cinturas.append(p["cintura"])
            quadris.append(p["quadril"])
            abdomens.append(p["abdomen"])

        # riscos
        riscos_cintura = [calcula_cintura(altura, c) for c in cinturas]
        riscos_quadril = [calcula_quadril(sexo, float(q), float(altura)) for q in quadris]
        riscos_abdomen = [calcula_abdomen(sexo, a) for a in abdomens]
        riscos_quad_cint = [cintura_quadril(sexo, idade, quadris[i], cinturas[i]) for i in range(len(cinturas))]

        # PESO AJUSTADO
        dados_antropometricos = dict(
            categorias_models.Antropometricos.objects.filter(usuario=user).values()[0])
        infos = {
            'idade': int((datetime.now().date() - dados_pessoais['nascimento']).days // 365.25),
            'sexo': dados_pessoais['sexo'],
            'altura': float(dados_pessoais['altura']),
            'abdomen': float(dados_antropometricos['abdomen']),
            'pulso': float(dados_antropometricos['pulso']),
            'peso': float(dados_antropometricos['peso']),
            'quadril': float(dados_antropometricos['quadril'])
        }

        parte = parte_a(infos['peso'], infos['abdomen'], infos['pulso'],
                        infos['sexo'], infos['quadril'], infos['altura'])
        gi = gordura_ideal(infos["sexo"], infos['idade'])
        parte = parte_a(infos['peso'], infos['abdomen'], infos['pulso'],
                        infos['sexo'], infos['quadril'], infos['altura'])

        ga = gordura_atual(infos['peso'], parte, infos['sexo'])
        gi = gordura_ideal(infos["sexo"], infos['idade'])
        gm = gordura_meta(gi, ga, infos["sexo"])
        pa = peso_ajustado(float(infos['peso']), float(ga), float(gm))

        # primeiro plano alimentar
        plano_1 = list(models.PlanoAlimentar.objects.filter(user=user).values().order_by("data_realizacao"))[0]
        per_gor_inicial = float(plano_1["percentual_gordura"]) - float(0.3)

        # metas
        lista_metas = {0: 0}
        lista_oks = {0: 0}
        if percentual_gordura_atual <= per_gor_inicial + 0.3:
            for i in range(80):
                lista_oks[i] = "--"

        i = 1
        while i < 80:
            lista_metas[i] = "-----"
            i += 1

        gm = gordura_meta(percentual_gordura_ideal, percentual_gordura_atual, sexo)
        pa = peso_ajustado(float(infos['peso']), float(percentual_gordura_atual), float(gm))

        i = 1
        while per_gor_inicial > gm:
            per_gor_inicial -= 0.3
            if percentual_gordura_atual <= per_gor_inicial:
                lista_oks[i] = "OK"
            else:
                lista_oks[i] = "--"
            lista_metas[i] = round(per_gor_inicial, 1)
            i += 1

        # cálculos finais de peso desejado
        P7 = peso
        P8 = percentual_gordura_atual
        P9 = P7 / 100 * P8
        R9 = percentual_gordura_ideal
        R10 = 100 - R9
        P10 = P7 - P9
        S10 = P10
        S9 = R9 * S10 / R10
        peso_desejado = S9 + S10

        # 🔹 Construir estrutura para la tabla (1–30 en la 1ª mitad, 31–60 en la 2ª)
        filas_metas = []
        for i in range(1, 31):  # 30 filas visibles
            j = i + 30           # empareja con la segunda mitad (31–60)
            m1 = {
                'num': i,
                'valor': lista_metas.get(i, '-----'),
                'estado': lista_oks.get(i, '--')
            }
            m2 = {
                'num': j,
                'valor': lista_metas.get(j, '-----'),
                'estado': lista_oks.get(j, '--')
            } if j in lista_metas else None
            filas_metas.append((m1, m2))

    
        # contexto
        context = {
            "nome_pessoa": usuario["nome"],
            "sobrenome_pessoa": usuario["sobrenome"],
            "peso": peso,
            "estado_peso": estado_peso,
            "massa_media": massa_magra,
            "per_gordura": per_gordura,
            "altura": round(altura/100, 2),
            "sexo": sexo,
            "peso_ideal": round(peso_desejado, 1),
            "peso_ideal_min": int(peso_ideal) - 1,
            "peso_ideal_max": int(peso_ideal) + 1,
            "percentual_gordura_ideal": round(percentual_gordura_ideal, 1),
            'percentual_gordura_real': round(percentual_gordura_atual, 1),
            "estado_per_gordura": estado_per_gordura,
            "peso_real_gordura": round(float(peso) - float(MM_real), 1),
            "peso_ideal_gordura": round(float(percentual_gordura_ideal) * float(MM_real) / float(100 - float(percentual_gordura_ideal)), 1),
            "peso_real_MM": round(MM_real, 1),
            "riscos_cintura": riscos_cintura,
            "riscos_quad_cint": riscos_quad_cint,
            "riscos_abdomen": riscos_abdomen,
            "riscos_quadril": riscos_quadril,
            "kcal_1": int(round((pa * 30) / 100) * 100),
            "kcal_2": int(plano["kcal"]),
            "kcal_3": int(plano["kcal_simples"]),
            #  "lista": lista_metas,
            #  "lista_oks": lista_oks,
            'filas_metas' :filas_metas,
            'idade':  idade,
        }
        for key in ['riscos_abdomen', 'riscos_cintura', 'riscos_quad_cint', 'riscos_quadril']:
            if isinstance(context.get(key), list) and len(context[key]) == 1:
                context[key] = context[key][0]
      
 
        if sexo == "masculino":
            self.template_name = "core/avn_compl_masculino.html"
        else:
            self.template_name = "core/avn_compl_fem.html"

        # Verificar plano alimentar (incompleto)
        passaram_7_dias = verifica_plano_alimentar(user)
        if not passaram_7_dias:
            if sexo == "masculino":
                self.template_name = "core/avn_parc_masculino.html"
            else:
                self.template_name = "core/avn_parc_fem.html"

        # DEVOLVER DIRECTO EL PDF (igual que CapaRelatorioView)
        return self._gerar_pdf(context)

    def _gerar_pdf(self, context):
        html_string = render_to_string(self.template_name, context)

        css = CSS(string='''
            @page { size: A4; margin: 20mm; }
            body { font-family: 'Open Sans', sans-serif; font-size: 11pt; color: #333; }
            .RC-item { background: #f7f9fc; border-radius: 8px; padding: 8px 14px; margin-bottom: 6px; }
            .RC-label { font-weight: 600; color: #1e3a8a; }
            .RC-desc { font-size: 10pt; color: #555; margin-left: 6px; }
        ''')

        with tempfile.NamedTemporaryFile(delete=True) as output:
            HTML(string=html_string, base_url=str(settings.BASE_DIR)).write_pdf(
                output.name,
                stylesheets=[css]
            )
            output.seek(0)
            pdf = output.read()

        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="relatorio_evolucao.pdf"'
        return response


class Calculadora_test(TemplateView):
    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            usuario = self.request.user.username
            if not list(models.Usuario.objects.filter(usuario=usuario).values()):
                messages.add_message(
                    self.request, messages.ERROR, "Usuário não encontrado")
                return redirect('login')

            usuario = list(models.Usuario.objects.filter(
                usuario=usuario).values())[0]
            context = {
                'usuario': usuario,
                'sem_avaliacao': self.request.GET.get('sem_avaliacao')
            }
        else:
            redirect("login")
        return render(self.request, 'core/calculadora_test.html', context)

    def post(self, *args, **kwargs):
        usuario = self.request.user.username
        usuario = list(models.Usuario.objects.filter(
            usuario=usuario).values())[0]

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
        MM_real = round(peso - (peso * ga/100), 1)
        # pegar gordura ideal
        gordura_i = gordura_ideal(sexo, idade)

        fator_multiplicação = 1 + gordura_i/100
        peso_ideal = round(MM_real * fator_multiplicação, 1)
        peso_gordura_ideal = round(peso_ideal - MM_real, 1)

        # gordura e peso perfeitos
        gordura_p = gordura_perfeita(sexo, idade)
        fator_multiplicação = 1 + gordura_p/100
        peso_perfeito = round(MM_real * fator_multiplicação, 1)
        peso_gordura_perfeita = round(peso_perfeito - MM_real, 1)

        context = {
            'usuario': usuario,
            'sem_avaliacao': self.request.GET.get('sem_avaliacao'),
            "percentual_gordura_atual": ga,
            "peso_atual": peso,
            "peso_ideal": peso_ideal,
            "peso_perfeito": peso_perfeito,
            "MM_real": MM_real,
            "peso_gordura_real": round(peso - MM_real, 1),
            "peso_gordura_ideal": round((gordura_i*MM_real)/(100-gordura_i), 1),
            "peso_gordura_perfeita": round((gordura_p*MM_real)/(100-gordura_p), 1),
            "gordura_ideal": gordura_i,
            "gordura_perfeita": gordura_p,
            "perder_bom": round(round(peso - MM_real, 1) - round((gordura_i*MM_real)/(100-gordura_i), 1), 2),
            "perder_perfeito": round(round(peso - MM_real, 1) - round((gordura_p*MM_real)/(100-gordura_p), 1), 2)
        }
        return render(self.request, 'core/calculadora_test.html', context)
    
from django.http import FileResponse, Http404
def descargar_archivo(request):
    ruta = '/app/datos.json'
    if not os.path.exists(ruta):
        raise Http404("Archivo no encontrado")
    return FileResponse(open(ruta, 'rb'), as_attachment=True)

