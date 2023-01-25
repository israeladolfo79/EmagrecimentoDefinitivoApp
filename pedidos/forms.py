from django import forms
from validate_docbr import CPF
from crispy_forms.helper import FormHelper
from core.models import Usuario
from django.contrib.auth.models import User
from categorias.models import DadosPessoais
from .models import Pedidos
from django.core.exceptions import ValidationError
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

class PedidosForm(forms.ModelForm):
    class Meta:
        model = Pedidos
        fields = [
            "cpf",
            "nome",
            "email",
            "preco_total",
            "pacote_de_planos",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_action = "."


class Cad(forms.ModelForm):
    usuario = forms.CharField(max_length=255, required=True, label="Nome de Usuário")
    nome = forms.CharField(max_length=255, required=True, label="Nome Completo")
    cpf = forms.CharField(max_length=11, required=True, label="CPF")
    nascimento = forms.DateField(required=True, label="Data de Nascimento")
    sexo = forms.ChoiceField(required=True,choices=(('masculino', "Masculino"), ('feminino', "Feminino")), label="Sexo")
    altura = forms.CharField(max_length=3,required=True, label="Altura")
    repetir_senha = forms.CharField(max_length=255, required=True, label="Repita a Senha",
    widget=forms.PasswordInput())
    class Meta:
        model = Usuario
        fields = [
            'usuario',
            'nome',
            'email',
            'senha',
            'repetir_senha',
    ]
    def __init__(self, *args, **kwargs):
        super(Cad, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
            
    #TODO: Criar todas as validações do método Clean
    
    def clean_cpf(self):
        cpf = self.cleaned_data['cpf']
        c = CPF()
        if not c.validate(cpf):
            raise ValidationError('Insira um cpf válido!')
        else:
            if DadosPessoais.objects.filter(cpf=cpf).exists() :
                self.add_error('cpf','Já existe um usuário com esse CPF. Vá até seção de Login e Insira seus dados')
            
    def clean_sexo(self):
        pass
    
    def clean(self):
        data = self.cleaned_data

        if data['senha'] != data['repetir_senha']:
            self.add_error('senha','As Senhas não conferem')

        if int(data['altura']) > 400:
            self.add_error('altura', "Informe uma altura válida")

        
    def clean_email(self):
        email = self.cleaned_data['email']
        if Usuario.objects.filter(email=email).exists():
            raise ValidationError("Este email já está em uso!")
        else:
            if User.objects.filter(email=email).exists():
                raise ValidationError("Este email já está em uso!")
            else:
                return email


    def clean_nascimento(self):
        nascimento = self.cleaned_data.get('nascimento')
        hoje = date.today()    
        if (hoje - relativedelta(years=18)) < nascimento:
            raise ValidationError("Você precisa ter mais que 18 anos para se inscrever neste site!")
        else:
            return nascimento

      
    def clean_nome(self):
        nome = self.cleaned_data.get('nome')
        if len(nome.split()) < 2:
            raise ValidationError("Insira seu nome completo!")
        else:
            return nome


    def clean_usuario(self):
        usuario = self.cleaned_data.get('usuario')

        if Usuario.objects.filter(usuario=usuario).exists():
            raise ValidationError("Este nome de usuário não está disponível!")
        else:
            if User.objects.filter(username=usuario).exists():
                raise ValidationError("Este nome de usuário não está disponível!")
            else:
                return usuario