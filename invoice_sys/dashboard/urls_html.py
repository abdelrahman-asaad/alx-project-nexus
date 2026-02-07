from django.urls import path
from . import views  # هيقرأ من views.py اللي فيه الحسابات

urlpatterns = [
    # نستخدم dashboard_page لأنها هي اللي فيها الـ context والبيانات
    path('', views.dashboard_page, name='dashboard_home'),
]