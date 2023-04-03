from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin
from .models import *


class UsuarioAdmin(admin.ModelAdmin):
    list_display = ("usuario","nome","sobrenome", "email", "avaliacoes")
    list_display_links = ("usuario",'email',)
    list_editable = ("avaliacoes",)
    search_fields = ("usuario","nome", "sobrenome", "email")

# class PaginaInicialAdmin(admin.ModelAdmin):
#     list_display = ("mensagem_1",)

class PlanoAlimentarAdmin(admin.ModelAdmin):
    list_display = ("user","data_realizacao", )
    list_filter = ("user", "data_realizacao")
    search_fields = ("user", "data_realizacao")
    
class DashBoardAdmin(admin.ModelAdmin):
    list_display = ("titulo_1","subtitulo_1", "titulo_2", "subtitulo_2", 'tamanho_titulo','tamanho_subtitulo')
    list_display_links = ('titulo_1',)
    list_editable = ("subtitulo_1", "titulo_2", "subtitulo_2", 'tamanho_titulo','tamanho_subtitulo' )

class VariaveisAdmin(admin.ModelAdmin):
    list_display = ('var_1', 'var_2', 'var_3',)

class MaterialDeApoioAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'texto',)
    summernote_fields = ('texto',)

@admin.register(CategoriaMaterialDeApoio)
class CategoriaMaterialDeApoioAdmin(admin.ModelAdmin):
    list_display = ('nome',)

@admin.register(Termos)
class TermosAdmin(SummernoteModelAdmin):
    list_display = ("termo_de_uso",)
    summernote_fields = ("termo_de_uso",)

@admin.register(Video)
class VideoAdmin(SummernoteModelAdmin):
    list_display = ("link",)

@admin.register(MaterialdeClientes)
class MaterialdeClientesAdmin(admin.ModelAdmin):
    list_display = ("usuario", "categoria")


admin.site.register(Usuario, UsuarioAdmin)
#admin.site.register(PaginaInicial, PaginaInicialAdmin)
admin.site.register(PlanoAlimentar, PlanoAlimentarAdmin)
admin.site.register(DashBoard, DashBoardAdmin)
admin.site.register(Variaveis, VariaveisAdmin)
admin.site.register(MaterialDeApoio, MaterialDeApoioAdmin)
