from django.urls import path
from . import views

urlpatterns = [
    path('', views.LoginView.as_view(), name='academias_login'),
    path("academia_dashboard/", views.AcademiaDashboardView.as_view(), name="academias_index"),
]