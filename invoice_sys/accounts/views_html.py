from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.cache import never_cache
# الصفحة الرئيسية (Landing Page)
def home_page(request):
    return render(request, "accounts/home.html")

# accounts/views_html.py

from django.views import View
from django.contrib.auth import get_user_model
from .tasks import notify_owner_user_verified

User = get_user_model()

class ActivateAccountHTMLView(View):
    template_name = "accounts/activate.html"

    def get(self, request):
        # عرض الفورم فقط
        return render(request, self.template_name)

    def post(self, request):
        email = request.POST.get("email")
        password = request.POST.get("password")
        context = {}

        try:
            user = User.objects.get(email=email)
            
            if user.has_usable_password():
                context['error'] = "Account already active. Please login."
            else:
                user.set_password(password)
                user.is_active = True
                user.save()
                # تشغيل مهمة خلفية
                notify_owner_user_verified.delay(user.email)
                context['message'] = "Password set successfully. Owner notified."
        except User.DoesNotExist:
            context['error'] = "Email not found in our records. Contact Admin."

        return render(request, self.template_name, context)

# صفحة التسجيل
def register_page(request):
    return render(request, "accounts/register.html")


# صفحة تسجيل الدخول
from django.shortcuts import redirect, render
from django.views.decorators.cache import never_cache

@never_cache
def login_page(request):
    # ✅ لو المستخدم عنده جلسة أو توكن مخزّن، ما يشوفش صفحة login
    if request.user.is_authenticated:
        return redirect("/invoices/")  # أو أي صفحة dashboard حسب الرول

    response = render(request, "accounts/login.html")
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response



# عرض المستخدمين (Owner / Manager)
def users_page(request):
    return render(request, "accounts/users.html")


# تحديث role مستخدم (Owner فقط)
def update_role_page(request, user_id):
    context = {"user_id": user_id}
    return render(request, "accounts/update_role.html", context)
