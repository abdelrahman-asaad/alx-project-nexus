from rest_framework.permissions import BasePermission

class IsManager(BasePermission):
    def has_permission(self, request, view):
        # التعديل: manager بدلاً من Manager
        return request.user.is_authenticated and request.user.role == "manager"

class IsSalesOrManager(BasePermission):
    def has_permission(self, request, view):
        # التعديل: lowercase roles
        return request.user.is_authenticated and request.user.role in ["sales", "manager"]

class IsOwnerOrManager(BasePermission):
    def has_permission(self, request, view):
        # التعديل: lowercase roles
        return request.user.is_authenticated and request.user.role in ["owner", "manager"]