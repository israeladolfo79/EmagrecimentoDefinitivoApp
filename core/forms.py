from django import forms
from . import models
from django.contrib.auth.models import User

class CadastroForm(forms.ModelForm):
    senha = forms.CharField(widget=forms.PasswordInput())
    repetir_senha = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = models.Usuario
        fields = [
            'usuario',
            'nome',
            'sobrenome',
            'email',
            'senha',
            'repetir_senha',
        ]


class PlanoALimentarForm(forms.ModelForm):
    class Meta:
        model = models.PlanoAlimentar
        exclude = ['',]

#form para o MaterialdeClientes
class MaterialdeClientesForm(forms.ModelForm):
    class Meta:
        model = models.MaterialdeClientes
        fields = [
            'usuario',
            'categoria',
            'material',
            'data_criacao'
    ]
    
