from django.contrib import admin
from .models import Payments

@admin.register(Payments)
class PaymentAdmin(admin.ModelAdmin):
    list_display=[
        "__str__",
        "order",
        "doc_number",
        "mercado_pago_id",
        "mercado_pago_status"
    ]
    list_filter = ["mercado_pago_status", "modified"]
    list_search = ["doc_number", "email", "mercado_pago_id"]