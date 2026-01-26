from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.cache import never_cache
# الصفحة الرئيسية (Landing Page)
def home_page(request):
    return render(request, "accounts/home.html")


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
