from rest_framework import generics, permissions
from .serializers import RegisterSerializer, UserSerializer, UpdateRoleSerializer, ActivateAccountSerializer
from django.contrib.auth import get_user_model
from .permissions import IsOwner, IsOwnerOrManager

User = get_user_model()


from rest_framework.views import APIView
from rest_framework.response import Response
from .tasks import notify_owner_user_verified
from rest_framework import status

class ActivateAccountView(APIView):
    # لا نضع IsAuthenticated هنا لأن المستخدم لم يسجل دخوله بعد
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        # استخدام السيريالايزر للتحقق من صحة الإيميل والباسورد
        serializer = ActivateAccountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        try:
            # البحث باستخدام __iexact لتجنب مشاكل الحروف الكبيرة والصغيرة
            user = User.objects.get(email__iexact=email)

            # المنطق المعتمد على unusable_password
            if user.has_usable_password():
                return Response(
                    {"message": "This account is already activated. Please sign in."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # تعيين الباسورد (سيصبح الآن usable) وتفعيل الحساب
            user.set_password(password)
            user.is_active = True
            user.save()

            # تشغيل مهمة الخلفية لإرسال الإيميل
            # نرسل الـ ID لضمان كفاءة Celery
            notify_owner_user_verified.delay(user.id)

            return Response(
                {"message": "Email activated successfully! You can now log in."},
                status=status.HTTP_200_OK
            )

        except User.DoesNotExist:
            return Response(
                {"error": "Email not found. Please contact your administrator."},
                status=status.HTTP_404_NOT_FOUND
            )


# List users (Owner فقط أو Owner + Manager على حسب متطلباتك)
class UserListView(generics.ListAPIView):  # ListAPIView >> GET
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsOwnerOrManager]  # Owner أو Manager هما اللي يقدروا يشوفوا المستخدمين



class UpdateUserRoleView(generics.UpdateAPIView): #to allow owner to set roles to users
    queryset = User.objects.all()
    serializer_class = UpdateRoleSerializer
    permission_classes = [IsOwner]
    # if you want only owner to promote sales to manager

class DeleteUserView(generics.DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsOwner]  # مثلاً: بس الـ Owner هو اللي يقدر يمسح مستخدم


# accounts/views.py
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserSerializer

class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
# This view returns the details of the currently authenticated user
#to clarify the current logged in user info so the frontend can use it especially for role-based access control

    #in the end there's a lot of use cases depending on business requirements#