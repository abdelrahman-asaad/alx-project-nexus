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
    permission_classes = [permissions.AllowAny]
    throttle_classes = [LoginThrottle]

    def post(self, request):
        serializer = ActivateAccountSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save() # هينفذ الـ save اللي إنت كاتبها في السيريالايزر
            
            # تشغيل المهمة خلفية باستخدام الـ ID
            notify_owner_user_verified.delay(user.id)
            
            return Response(
                {"message": "Email activated successfully! You can now log in."},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from rest_framework.views import APIView
from rest_framework.response import Response
from .throttles import LoginThrottle # استيراد الكلاس اللي عملناه

class LoginView(APIView):
    throttle_classes = [LoginThrottle]  # تطبيق الحماية هنا
    
    def post(self, request):
        # الكود بتاع تسجيل الدخول (التحقق من الاسم والباسورد)
        return Response({"message": "Login successful"})
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