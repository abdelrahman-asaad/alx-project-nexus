from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import get_user_model
from django.views.decorators.cache import never_cache
from .tasks import notify_owner_user_verified
from .serializers import ActivateAccountSerializer

User = get_user_model()

# الصفحة الرئيسية
def home_page(request):
    return render(request, "accounts/home.html")

class ActivateAccountHTMLView(View):
    template_name = "accounts/activate.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
       
        serializer = ActivateAccountSerializer(data=request.POST) # validation of data from serializer
        if serializer.is_valid():
            user = serializer.save()
            # إرسال الـ ID للمهمة الخلفية
            notify_owner_user_verified.delay(user.id)
            return render(request, self.template_name, {"message": "Success! Account activated."})
        else:
            # استخراج أول رسالة خطأ بشكل نظيف
            error_msg = list(serializer.errors.values())[0][0]
            return render(request, self.template_name, {"error": error_msg})

@never_cache
def login_page(request):
    response = render(request, "accounts/login.html")
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response

# ملاحظة: يفضل إضافة @login_required هنا لاحقاً
def users_page(request):
    return render(request, "accounts/users.html")

def update_role_page(request, user_id):
    return render(request, "accounts/update_role.html", {"user_id": user_id})

def register_page(request):
    return render(request, "accounts/register.html")