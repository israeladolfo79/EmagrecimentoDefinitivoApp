from django.urls import path
from . import views

urlpatterns = [
    path('', views.LoginView.as_view(), name='academias_login'),
    path('logout/', views.logout_view, name='academias_logout'),
    path("academia_dashboard/", views.AcademiaDashboardView.as_view(), name="academias_index"),
    path("cadastrar_aluno/", views.CadastrarAluno.as_view(), name="cadastrar_aluno"),
    path("calculadora_academia/", views.Calculadora.as_view(), name="calculadora_academia"),
    path("consulta_alunos/", views.ConsultaAluno.as_view(), name="consulta_alunos"),
    path('avaliacao_nutricional_academia/<str:user>', views.RelatorioEvolucaoAcademia.as_view(), name='academia_avaliacao_nutricional'),
    path("relatorio_evolucao_academia/<str:user>", views.EvolucaoFinal.as_view(), name="relatorio_evolucao_academia"),
]