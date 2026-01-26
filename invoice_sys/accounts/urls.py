from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, UserListView, UpdateUserRoleView , DeleteUserView
from .views import MeView
urlpatterns = [
    #api/accounts/
    path('register/', RegisterView.as_view(), name='register'), #POST
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'), # login
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("users/<int:pk>/role/", UpdateUserRoleView.as_view(), name="update-user-role"),
    path('users/', UserListView.as_view(), name='user-list'), #GET
    path('users/<int:pk>/delete/', DeleteUserView.as_view(), name='delete-user'),
    path("me/", MeView.as_view(), name="me"),
    #GET api/accounts/users

    #api/clients/

]
