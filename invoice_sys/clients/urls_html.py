from django.urls import path
from . import views_html  # لو عندك views_html.py في نفس app

urlpatterns = [
    # مثال بسيط
    path('', views_html.client_list, name='client_list'),
]
