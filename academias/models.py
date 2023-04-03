from django.db import models

class Academia(models.Model):
    cnpj = models.CharField(max_length=100, primary_key=True)
    nome = models.CharField(max_length=100)
    endereco = models.CharField(max_length=100)
    telefone = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    senha = models.CharField(max_length=100)
    dia_expiracao = models.DateField(null=True, blank=True)
    avaliacoes_disponiveis = models.IntegerField(default=0)
    def __str__(self):
        return self.nome

