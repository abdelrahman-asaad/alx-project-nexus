from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model

# --- 🚀 استيراد أدوات التوثيق (Swagger Tools) ---
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers

from .serializers import (
    RegisterSerializer, UserSerializer, 
    UpdateRoleSerializer, ActivateAccountSerializer
)
from .permissions import IsOwner, IsOwnerOrManager
from .throttles import LoginThrottle
from .tasks import notify_owner_user_verified

User = get_user_model()

# 📧 تفعيل الحساب
class ActivateAccountView(APIView):
    permission_classes = [permissions.AllowAny]
    # تطبيق الـ Throttle لمنع الهجمات المتكررة (Brute Force)
    throttle_classes = [LoginThrottle]

    # 📝 نغشش Swagger إن الـ Response عبارة عن رسالة نجاح
    @extend_schema(
        request=ActivateAccountSerializer,
        responses={
            200: inline_serializer(
                name='ActivateAccountResponse',
                fields={'message': serializers.CharField()}
            ),
            400: inline_serializer(
                name='ActivateAccountError',
                fields={'error': serializers.CharField()}
            )
        },
        description="تفعيل الحساب عن طريق الكود المرسل للإيميل"
    )
    def post(self, request):
        serializer = ActivateAccountSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # تشغيل مهمة Celery في الخلفية لإرسال إشعار للمدير
            notify_owner_user_verified.delay(user.id)
            
            return Response(
                {"message": "Email activated successfully! You can now log in."},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 🔑 تسجيل الدخول
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [LoginThrottle] 
    
    @extend_schema(
        responses={200: inline_serializer(name='LoginSuccess', fields={'message': serializers.CharField()})},
        description="تسجيل الدخول للنظام"
    )
    def post(self, request):
        # الكود الخاص بالتحقق يتم عادة عبر الـ Token (مثل JWT)
        return Response({"message": "Login successful"})


# 👤 بيانات المستخدم الحالي (Profile)
class MeView(APIView):
    permission_classes = [IsAuthenticated]

    # 📝 هنا بنحدد إن الـ Swagger يستخدم الـ UserSerializer تلقائياً
    @extend_schema(
        responses={200: UserSerializer},
        description="جلب بيانات المستخدم المسجل حالياً (Role, Email, etc.)"
    )
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


# 📋 عرض قائمة المستخدمين (للمديرين فقط)
class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsOwnerOrManager]
    # ملاحظة: الـ generics مش محتاجة extend_schema لأنها بتعرف السيريالايزر لوحدها


# 🆙 تحديث صلاحيات المستخدم (لصاحب العمل فقط)
class UpdateUserRoleView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UpdateRoleSerializer
    permission_classes = [IsOwner]


# ❌ مسح مستخدم
class DeleteUserView(generics.DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer # يفضل استخدام السيريالايزر لعرض البيانات قبل المسح
    permission_classes = [IsOwner]