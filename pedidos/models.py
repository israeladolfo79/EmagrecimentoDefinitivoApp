from enum import unique
from django.db import models
from localflavor.br.models import BRCPFField
from model_utils.models import TimeStampedModel


class PacoteDeVenda(models.Model):
    class Meta: 
        verbose_name_plural = "Pacotes à Venda"
    titulo = models.CharField(max_length=250, verbose_name="Nome do Pacote")
    preco = models.IntegerField(verbose_name="Preço do pacote")
    imagem = models.ImageField(upload_to="produtos/imgs/%Y/%m", verbose_name="Imagem do Pacote")
    descricao = models.TextField(verbose_name="Descrição do pacote")
    quantidade = models.IntegerField(verbose_name="Quantidade de planos que será adicionado neste pacote")
    quantidade_de_dias = models.IntegerField(verbose_name="Quantidade de dias a serem adicionados")
    ativo = models.BooleanField(default=True, verbose_name="Pacote está ativo?")

    def __str__(self):
        return self.titulo

class Pedidos(TimeStampedModel):
    cpf = BRCPFField("CPF")
    nome = models.CharField(verbose_name="Nome Completo", max_length=250)
    email = models.EmailField(verbose_name="Email")
    pacote_de_planos = models.ForeignKey(
        PacoteDeVenda,
        on_delete=models.DO_NOTHING, 
        verbose_name="Pacote Selecionado",
        related_name="pacote_planos"
    )
    preco_total = models.DecimalField(max_digits=10,decimal_places=2, verbose_name="Preço total")
    pago = models.BooleanField(default=False)

    class Meta:
        ordering = ("-created", )
        verbose_name_plural = "Pedidos"

    def get_total_price(self):
        total_cost = self.preco_total
        return total_cost

    def get_description(self):
        return f"1x {self.pacote_de_planos.titulo}"
    
    def __str__(self) -> str:
        return f"Pedido {self.id}"
