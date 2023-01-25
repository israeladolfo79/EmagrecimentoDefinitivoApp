from django.urls import path
from django.contrib.auth.decorators import login_required
from .import views

app_name = "pedidos"

urlpatterns = [
    path("", login_required(views.OrderCreateView.as_view()), name="pedido"),
    path("cad_order", views.OrderCad.as_view(), name="ord"),
]