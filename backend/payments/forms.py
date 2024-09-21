import mercadopago
from django import forms
from django.conf import settings

from .models import Payments as Payment
from categorias.models import DadosPessoais
from core.models import Usuario

from datetime import timedelta,datetime

class PaymentForm(forms.ModelForm):
    token = forms.CharField()

    class Meta:
        model = Payment
        fields = [
            "transaction_amount",
            "installments",
            "payment_method_id",
            "email",
            "doc_number",
        ]

    def __init__(self, *args, **kwargs):
        self.order = kwargs.pop("order")
        super().__init__(*args, **kwargs)

    def clean_transaction_amount(self):
        transaction_amount = self.cleaned_data["transaction_amount"]
        if float(transaction_amount) != float(self.order.get_total_price()):
            raise forms.ValidationError(
                "Transaction Amount não bate com o banco de dados!"
            )
        return transaction_amount

    def save(self):
        cd = self.cleaned_data
        mp = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)
        payment_data = {
            "transaction_amount": float(self.order.get_total_price()),
            "token": cd["token"],
            "description": self.order.get_description(),
            "installments": cd["installments"],
            "payment_method_id": cd["payment_method_id"],
            "payer": {
                "email": cd["email"],
                "identification": {"type": "CPF", "number": cd["doc_number"]},
            },
        }
        payment = mp.payment().create(payment_data)

        if payment["status"] == 201:
            self.instance.order = self.order
            self.instance.mercado_pago_id = payment["response"]["id"]
            self.instance.mercado_pago_status_detail = payment["response"][
                "status_detail"
            ]
            self.instance.mercado_pago_status = payment["response"]["status"]

            if payment["response"]["status"] == "approved":
                self.order.paid = True
                self.order.save()
            self.instance.save()


class UpdatePaymentForm(forms.Form):
    action = forms.CharField()
    data = forms.JSONField()
    def save(self):
        cd = self.cleaned_data
        mp = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)
        if cd["action"] == "payment.updated":
            mercado_pago_id = cd["data"]["id"]
            payment = Payment.objects.get(mercado_pago_id=mercado_pago_id)
            payment_mp = mp.payment().get(mercado_pago_id)
            payment.mercado_pago_status = payment_mp["response"]["status"]
            payment.mercado_pago_status_detail = payment_mp["response"]["status_detail"]

            #pegar usuario do pedido
            cpf_pagamento = payment.order.cpf
            usuario = DadosPessoais.objects.get(cpf=cpf_pagamento).user
            usuario = Usuario.objects.get(usuario=usuario)
            
            
            if payment_mp["response"]["status"] == "approved":
                #Se o estado do pagamento no banco NÃO for aprovado:
                if payment.mercado_pago_status != "approved":
                    #pegar usuario do pedido
                    cpf_pagamento = payment.order.cpf
                    usuario = DadosPessoais.objects.get(cpf=cpf_pagamento).user
                    usuario = Usuario.objects.get(usuario=usuario)
                    
                    #pegar quantidade de planos que devem ser adicionados
                    quantidade_a_ser_adicionada = payment.order.pacote_de_planos.quantidade
                    quantidade_dias = payment.order.pacote_de_planos.quantidade_de_dias
                    if quantidade_dias < 40:
                        usuario.tipo_plano = 1
                    else:
                        usuario.tipo_plano = 2
                    
                    #adicionar planos ao usuário
                    usuario.avaliacoes += quantidade_a_ser_adicionada
                    d=usuario.dias_restantes
                    a = datetime.today() if d == "" else datetime.strptime(d,"%d/%m/%Y")
                    dias_r = a
                    usuario.dias_restantes = (dias_r + timedelta(days=quantidade_dias)).strftime("%d/%m/%Y")
                    usuario.save()
                payment.order.paid = True
            else:
                payment.order.paid = False

            payment.order.save()
            payment.save()
