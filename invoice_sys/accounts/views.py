from rest_framework import generics, permissions
from .serializers import RegisterSerializer, UserSerializer, UpdateRoleSerializer
from django.contrib.auth import get_user_model
from .permissions import IsOwner, IsOwnerOrManager

User = get_user_model()


# Register new user
class RegisterView(generics.CreateAPIView):  # CreateAPIView >> POST
    queryset = User.objects.all() 
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]  # أي حد يقدر يعمل Register

# or permission_classes = [permissions.IsAdminUser]
# to allow only admin to create users and set their roles 
# and that's the best practice in real-world applications
# i just allowed anyone to register for testing purposes

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