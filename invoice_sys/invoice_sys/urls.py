"""
URL configuration for invoice_sys project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt
from graphene_django.views import GraphQLView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
# تأكد من إنشاء ملف schema.py رئيسي يجمع كل الـ schemas من التطبيقات
# من خلال إنشاء Root Schema (سأوضحها لك بالأسفل)


# سنقوم بإنشاء نسخة من الـ sawgger بدون Throttling
class CustomSpectacularAPIView(SpectacularAPIView):
    throttle_classes = [] # تعطيل الـ Throttle لهذا المسار تحديداً

class CustomSpectacularSwaggerView(SpectacularSwaggerView):
    throttle_classes = [] # تعطيل الـ Throttle لواجهة المستخدم
urlpatterns = [
    path('admin/', admin.site.urls),
    
    # 🔗 GraphQL Endpoint (البوابة الجديدة)
    # csrf_exempt مهمة هنا عشان تقدر تبعت Queries من غير مشاكل الـ CSRF في البداية
    path("graphql/", csrf_exempt(GraphQLView.as_view(graphiql=True))),

    # الروابط الخاصة بالـ Swagger بدون Throttling
    path('api/schema/', CustomSpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', CustomSpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),


    # 🚀 API Endpoints (DRF)
    path('api/accounts/', include('accounts.urls')),
    path('api/products/', include('products.urls')),
    path('api/invoices/', include('invoices.urls')),
    path('api/clients/', include('clients.urls')), # لاحظ توحيد الـ lowercase في المسار
    path('api/payments/', include('payments.urls')),
    path('api/dashboard/', include('dashboard.urls')),
    path('api/auditlogs/', include('auditlog.urls')),

    # 🖥️ HTML Pages
    path('accounts/', include('accounts.urls_html')),
    path('products/', include('products.urls_html')),
    path('invoices/', include('invoices.urls_html')),
    path('clients/', include('clients.urls_html')),
    path('payments/', include('payments.urls_html')),
    # يفضل إضافة مسار الـ dashboard هنا أيضاً لو كانت صفحة HTML
    path('dashboard/', include('dashboard.urls_html')), 
]


