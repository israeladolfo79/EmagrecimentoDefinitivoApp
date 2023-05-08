"""projeto URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Routers provide an easy way of automatically determining the URL conf.
from rest_framework import routers
from core.api import viewsets as coreViewsets
from categorias.api import viewsets as categoriasViewsets

route = routers.DefaultRouter()

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include("core.urls")),
    path('academias/', include("academias.urls")),
    path('pedido/', include("pedidos.urls")),
    path('pagamentos/', include("payments.urls")),

    path('summernote/', include('django_summernote.urls')),

    path('rest-auth/', include('rest_auth.urls')),

    path('apis/', include(route.urls)),
    path('apis/login',coreViewsets.LoginViewSets.as_view(), name="login_apis"),
    path('apis/dados_pessoais',categoriasViewsets.DadosPessoaisViewSets.as_view(), name='point_dados_pessoais'),
    path('apis/doencas',categoriasViewsets.DoencasViewSets.as_view(), name='point_doencas'),
    path('apis/medicamentos',categoriasViewsets.MedicamentosViewSets.as_view(), name='point_medicamentos'),
    path('apis/cirurgias',categoriasViewsets.CirurgiaViewSets.as_view(), name='point_cirurgias'),
    path('apis/exame_sangue',categoriasViewsets.ExameDeSangueViewSets.as_view(), name='point_exame_sangue'),
    path('apis/intestino',categoriasViewsets.IntestinoViewSets.as_view(), name='point_intestino'),
    path('apis/sono',categoriasViewsets.SonoViewSets.as_view(), name='point_sono'),
    path('apis/alcool',categoriasViewsets.AlcoolViewSets.as_view(), name='point_alcool'),
    path('apis/suplemento',categoriasViewsets.SuplementoViewSets.as_view(), name='point_suplemento'),
    path('apis/ciclos_menstruais',categoriasViewsets.CiclosMenstruaisViewSets.as_view(), name='point_ciclos_menstruais'),
    path('apis/antropometricos',categoriasViewsets.AntropometricosViewSets.as_view(), name='point_antropometricos'),
    path('apis/horarios',categoriasViewsets.HorariosViewSets.as_view(), name='point_horarios'),
    path('apis/exercicios',categoriasViewsets.ExerciciosViewSets.as_view(), name='point_exercicios'),
    path('apis/plano_alimentar',coreViewsets.PlanoAlimentarViewset.as_view(), name='point_plano_alimentar'),
    path('apis/material_apoio',coreViewsets.MaterialApoioViewSet.as_view(), name='point_materiais'),
    path('apis/calculadora',coreViewsets.CalculadoraViewSet.as_view(), name='point_calculadora'),
    path('apis/pacotes_venda',coreViewsets.PlanosOferecidosViewSet.as_view(), name='point_pacotes'),
    path('apis/cria_pedido',coreViewsets.CriaPedidoViewSet.as_view(), name='point_cria_pedido'),
    path('apis/cria_payment',coreViewsets.CriaPaymentViewSet.as_view(), name='point_cria_pagamento'),
    path('apis/usuario_details',coreViewsets.UsuarioViewSets.as_view(), name='point_usuario_details'),
    path('apis/relatorio_evolucao',coreViewsets.RelatorioEvolucao.as_view(), name='point_relatorio_evolucao'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

handler404 = "core.views.error_404"
handler500 = "core.views.error_500"