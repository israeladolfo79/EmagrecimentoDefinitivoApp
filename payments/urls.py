from django.urls import path

from .views import (
    PaymentCreateView,
    PaymentFailureView,
    PaymentPendingView,
    PaymentSuccessView,
    PaymentMethod,
    payment_webhook,
)

app_name = "payments"

urlpatterns = [
    path("process/", PaymentCreateView.as_view(), name="process"),
    path("payment_method/", PaymentMethod.as_view(), name="payment_method"),
    path("failure/", PaymentFailureView.as_view(), name="failure"),
    path("pending/", PaymentPendingView.as_view(), name="pending"),
    path("success/", PaymentSuccessView.as_view(), name="success"),
    path("webhook/", payment_webhook, name="webhook"),
]
