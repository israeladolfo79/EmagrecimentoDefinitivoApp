import json
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils.functional import cached_property
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, TemplateView
from pedidos.models import Pedidos as Order
from core.models import Usuario
from categorias.models import DadosPessoais
import uuid

from .forms import PaymentForm, UpdatePaymentForm
from .models import Payments as Payment

import mercadopago
from datetime import datetime, timedelta


class PaymentMethod(TemplateView):
    template_name = 'payments/select_method.html'
    def get(self, *args, **kwargs):
        print(settings.MERCADO_PAGO_ACCESS_TOKEN)
        sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)

        idempotency_key = str(uuid.uuid4())

    # Configuração de requisição com chave de idempotência
        request_options = mercadopago.config.RequestOptions()
        request_options.custom_headers = {
            'x-idempotency-key': idempotency_key  # Chave única gerada dinamicamente
        }

        order_id = self.request.session.get("order_id")
        order = get_object_or_404(Order, id=order_id)
        preference_data = {
                "notification_url": "https://emagrecimentodefinitivo.app.br/pagamentos/webhook/",
                "back_urls": {
                            'failure': 'https://emagrecimentodefinitivo.app.br/pagamentos/failure/',
                            'pending': 'https://emagrecimentodefinitivo.app.br/pagamentos/pending/',
                            'success': 'https://emagrecimentodefinitivo.app.br/pagamentos/success/',
                        },
                "items": [
                    {
                        "title": f"{order.pacote_de_planos.titulo}",
                        "quantity": 1,
                        "unit_price": float(order.preco_total),
                        

                    }
                ]
            }
        preference_response = sdk.preference().create(preference_data, request_options)
        preference = preference_response["response"]
        init = preference['init_point']
        context = {
            'init': init,
            'preference_id': preference['id'],
            'PUBLIC_KEY': settings.MERCADO_PAGO_PUBLIC_KEY,
            'order': order
        }

        return render(self.request, self.template_name, context)

class PaymentCreateView(CreateView):
    model = Payment
    form_class = PaymentForm

    @cached_property
    def order(self):
        order_id = self.request.session.get("order_id")
        order = get_object_or_404(Order, id=order_id)
        return order

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs["order"] = self.order
        return form_kwargs

    def form_valid(self, form):
        form.save()
        redirect_url = "payments:failure"
        status = form.instance.mercado_pago_status

        if status == "approved":
            #pegar usuario atual
            user = self.request.user.username
            usuario = Usuario.objects.get(usuario=self.request.user.username)

            #pegar quantidade a ser adicionada
            order_id = self.request.session.get("order_id")
            order = get_object_or_404(Order, id=order_id)
            
            quantidade_a_ser_adicionada = order.pacote_de_planos.quantidade
            quantidade_de_dias = order.pacote_de_planos.quantidade_de_dias
            if quantidade_de_dias < 40:
                usuario.tipo_plano = 1
            else:
                usuario.tipo_plano = 2
            #adicionar aos planos do usuario a quantidade comprada
            usuario.avaliacoes += quantidade_a_ser_adicionada
            d=usuario.dias_restantes
            a = datetime.today() if d == "" else datetime.strptime(d,"%d/%m/%Y")
            dias_r = a
            usuario.dias_restantes = (dias_r + timedelta(days=quantidade_de_dias)).strftime("%d/%m/%Y")
            order.pago=True
            order.save()
            usuario.save()
            redirect_url = "payments:success"

        if status == "in_process":
            redirect_url = "payments:pending"

        if status and status != "rejected":
            del self.request.session["order_id"]
        return redirect(redirect_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["order"] = self.order
        context["publishable_key"] = settings.MERCADO_PAGO_PUBLIC_KEY
        return context

class PaymentFailureView(TemplateView):
    template_name = "payments/failure.html"


class PaymentPendingView(TemplateView):
    template_name = "payments/pending.html"
    def get(self,*args, **kwargs):
            order_id = self.request.session.get("order_id")
            order = get_object_or_404(Order, id=order_id)
            context={}
            Payment.objects.create(
                order = order,
                transaction_amount = order.preco_total,
                installments = 1,
                payment_method_id = self.request.GET.get('payment_type'),
                email = order.email,
                doc_number = order.cpf,
                mercado_pago_id = self.request.GET.get('payment_id'),
                mercado_pago_status = self.request.GET.get('status'),
                mercado_pago_status_detail = self.request.GET.get('collection_status'),
            )
            mp = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)
            mercado_pago_id = self.request.GET.get('payment_id')
            payment = Payment.objects.get(mercado_pago_id=mercado_pago_id)
            payment_mp = mp.payment().get(mercado_pago_id)
            payment.mercado_pago_status = payment_mp["response"]["status"]
            payment.mercado_pago_status_detail = payment_mp["response"]["status_detail"]
            #pegar usuario do pedido
            cpf_pagamento = payment.order.cpf
            usuario = DadosPessoais.objects.get(cpf=cpf_pagamento).user
            usuario = Usuario.objects.get(usuario=usuario)
                
                
            if payment.mercado_pago_status == "approved":
                #pegar usuario do pedido
                cpf_pagamento = payment.order.cpf
                usuario = DadosPessoais.objects.get(cpf=cpf_pagamento).user
                usuario = Usuario.objects.get(usuario=usuario)
                
                #pegar quantidade de planos que devem ser adicionados
                quantidade_a_ser_adicionada = payment.order.pacote_de_planos.quantidade
                quantidade_dias = payment.order.pacote_de_planos.quantidade_de_dias
                context['quantidade_dias'] = quantidade_dias
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
            del self.request.session["order_id"] 
            
            return render(self.request, self.template_name)


class PaymentSuccessView(TemplateView):
    template_name = "payments/success.html"
    def get(self, *args, **kwargs):
        #pegar quantidade a ser adicionada
        order_id = self.request.session.get("order_id")
        order = get_object_or_404(Order, id=order_id)
        usuario = Usuario.objects.get(usuario=self.request.user.username)

        quantidade_a_ser_adicionada = order.pacote_de_planos.quantidade
        quantidade_de_dias = order.pacote_de_planos.quantidade_de_dias
        if quantidade_de_dias < 40:
            usuario.tipo_plano = 1
        else:
            usuario.tipo_plano = 2
        #adicionar aos planos do usuario a quantidade comprada
        usuario.avaliacoes += quantidade_a_ser_adicionada
        d=usuario.dias_restantes
        a = datetime.today() if d == "" else datetime.strptime(d,"%d/%m/%Y")
        dias_r = a
        usuario.dias_restantes = (dias_r + timedelta(days=quantidade_de_dias)).strftime("%d/%m/%Y")
        order.pago=True

        order.save()
        usuario.save()


        del self.request.session["order_id"]
        return render(self.request, self.template_name)


@csrf_exempt
@require_POST
def payment_webhook(request):
    data = json.loads(request.body)
    form = UpdatePaymentForm(data)
    if form.is_valid():
        form.save()

    return JsonResponse({"received": "True"})
