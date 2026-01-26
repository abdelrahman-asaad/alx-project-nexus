from django.urls import path
from . import views_html

urlpatterns = [
    path('', views_html.products_page, name='products_page'),
]
