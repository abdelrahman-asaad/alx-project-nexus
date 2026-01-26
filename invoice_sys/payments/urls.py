from django.urls import path
from .views import PaymentListCreateView

urlpatterns = [
    path("", PaymentListCreateView.as_view(), name="payment-list-create"),
]
