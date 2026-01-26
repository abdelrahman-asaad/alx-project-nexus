from django.urls import path
from . import views_html

urlpatterns = [
    path("", views_html.invoice_list_page, name="invoice_list_page"),
    path("create/", views_html.invoice_create_page, name="invoice_create_page"),
]
