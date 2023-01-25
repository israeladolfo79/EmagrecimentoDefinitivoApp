from django.contrib import admin
from .models import *

class DadospessoaisAdmin(admin.ModelAdmin):
    list_display = ("user","nome_completo","cpf", 'sexo')
    list_filter = ("sexo",)
    search_fields = ("nome_completo", "cpf")

class DoencaAdmin(admin.ModelAdmin):
    list_display = ("user",'refluxo',
                    'gastrite',
                    'figado',
                    'renal',
                    'tireoide',
                    'pressao_alta',
                    'diabetes',
                    'colesterol',
                    'infos_adicionais'
)

class MedicamentoAdmin(admin.ModelAdmin):
    list_display = ("user",'medicamentos',)

class CirurgiaAdmin(admin.ModelAdmin):
    list_display = ("user",'cirurgias',)

class ExameSangueAdmin(admin.ModelAdmin):
    list_display = ("user",'exame', 'alteracoes')

class IntestinoAdmin(admin.ModelAdmin):
    list_display = ("user",'cor_urina', )

class SonoAdmin(admin.ModelAdmin):
    list_display = ("user",'acorda_noite', )

class AlcoolAdmin(admin.ModelAdmin):
    list_display = ("user",'consome_alcool', )

class SuplementoAdmin(admin.ModelAdmin):
    list_display = ("user",'creatina', )

class CicloMenstrualAdmin(admin.ModelAdmin):
    list_display = ("user",'quantos_dias_menstrua', )

class AntropometricasAdmin(admin.ModelAdmin):
    list_display = ("user", )

class HorariosAdmin(admin.ModelAdmin):
    list_display = ("user",'treino', )

class ExercicioAdmin(admin.ModelAdmin):
    list_display = ("user",'treino', )

admin.site.register(DadosPessoais, DadospessoaisAdmin)
admin.site.register(Antropometricos, AntropometricasAdmin)
admin.site.register(Doenca, DoencaAdmin)
admin.site.register(Medicamento, MedicamentoAdmin)
admin.site.register(Cirurgia, CirurgiaAdmin)
admin.site.register(ExameSangue, ExameSangueAdmin)
admin.site.register(Intestino, IntestinoAdmin)
admin.site.register(Sono, SonoAdmin)
admin.site.register(Alcool, AlcoolAdmin)
admin.site.register(Suplemento, SuplementoAdmin)
admin.site.register(CicloMenstrual, CicloMenstrualAdmin)
admin.site.register(Horarios, HorariosAdmin)
admin.site.register(Exercicios, ExercicioAdmin)

