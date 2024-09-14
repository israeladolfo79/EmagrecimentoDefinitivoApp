from django.contrib import admin
from .models import Academia

# Register your models here.

class AcademiaAdmin(admin.ModelAdmin):
    list_display = ('cnpj', 'nome', 'endereco', 'telefone', 'email')
    search_fields = ('cnpj', 'nome', 'endereco', 'telefone', 'email')
admin.site.register(Academia, AcademiaAdmin)
