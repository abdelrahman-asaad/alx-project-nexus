from django.urls import path
from .views import (
    InvoiceListCreateView,
    InvoiceRetrieveUpdateDeleteView,
    InvoicePDFView
)

urlpatterns = [
    path("", InvoiceListCreateView.as_view(), name="invoice-list-create"),  
    path("<int:pk>/", InvoiceRetrieveUpdateDeleteView.as_view(), name="invoice-detail"),  
    path("<int:pk>/pdf/", InvoicePDFView.as_view(), name="invoice-pdf"),  
]
