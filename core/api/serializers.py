from rest_framework import serializers
from core import models
from django.contrib.auth.models import User

from pedidos import models as models_pacotes
from payments import models as models_payments


class UsuarioSerializer(serializers.ModelSerializer):
    def validate(self, data):
        if len(data['usuario'])<5:
            raise serializers.ValidationError({'usuario': 'Usuario deve conter ao menos 5 caracteres'})

        if len(data['senha']) < 5:
            raise serializers.ValidationError({'senha': 'Senha deve conter ao menos 5 caracteres'})

        if data['senha'] != data['repetir_senha']:
            raise serializers.ValidationError({'senha': 'As senhas não coincidem'})
        salvar = True
        if User.objects.filter(username=data['usuario']).exists():
            salvar = False
            raise serializers.ValidationError({'usuario': 'Este nome de usuário já está em uso'})

        if User.objects.filter(email=data['email']).exists():
            salvar = False
            raise serializers.ValidationError({'email': 'Este email já está em uso'})

        if salvar == True:
            usuario = User.objects.create_user(
                username=data['usuario'], 
                email=data['email'],
                first_name=data['nome'],
                last_name=data['sobrenome'],
                password=data['senha'],
                )
            usuario.save()
        return data
    class Meta:
        model = models.Usuario
        fields = ('usuario', 'nome', 'sobrenome', 'email', 'senha', 'repetir_senha')

class LoginSerializer(serializers.ModelSerializer):
    def validate(self, data):
        if not User.objects.filter(username=data['usuario']).exists():
            raise serializers.ValidationError({'usuario': 'Usuário não encontrado'})
        else:
            usuario = User.objects.get(username=data['usuario'])
            if usuario.senha != data['senha']:
                raise serializers.ValidationError({'senha': 'Senha Incorreta!'})
        print(data)
        return data
    class Meta:
        model = models.Usuario
        fields = ('usuario', 'senha')


class PlanoAlimentarSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PlanoAlimentar
        fields = "__all__"

class MaterialApoioSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.MaterialDeApoio
        fields = "__all__"

class PacoteDeVendaSerializer(serializers.ModelSerializer):
    class Meta:
        model = models_pacotes.PacoteDeVenda
        fields = "__all__"

class CriaPedidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models_pacotes.Pedidos
        fields = "__all__"

class CriaPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models_payments.Payments
        fields = "__all__"