from django.urls import path
from . import views_html

urlpatterns = [
    path('', views_html.home_page, name='home_page'),
    path('register/', views_html.register_page, name='register_page'),
    path('login/', views_html.login_page, name='login_page'),
    path('users/', views_html.users_page, name='users_page'),
    path('users/<int:user_id>/update-role/', views_html.update_role_page, name='update_role_page'),
]
