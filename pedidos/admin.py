from django.contrib import admin
from payments.models import Payments
from .models import Pedidos,PacoteDeVenda
from django_summernote.admin import SummernoteModelAdmin


@admin.register(PacoteDeVenda)
class PacoteDeVendaAdmin(SummernoteModelAdmin):
    list_display=['titulo',]
    summernote_fields = ('descricao',)

class PaymentInline(admin.TabularInline):
    model = Payments
    can_delete = False
    readonly_fields = (
        "email",
        "doc_number",
        "transaction_amount",
        "installments",
        "payment_method_id",
        "mercado_pago_id",
        "mercado_pago_status",
        "mercado_pago_status_detail",
        "modified",
    )
    ordering = ("-modified",)

    def has_add_permission(self, request, obj):
        return False

@admin.register(Pedidos)
class PedidoAdmin(admin.ModelAdmin):
    list_display=["__str__", "nome", "email", "cpf", "pago", "created", "modified"]
    list_filter=["pago", "created", "modified"]
    search_fields=["nome", "cpf", "email"]
    inlines = [PaymentInline]
