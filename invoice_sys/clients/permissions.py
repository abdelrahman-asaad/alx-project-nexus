from rest_framework.permissions import BasePermission

class IsManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "Manager"

class IsSalesOrManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ["Sales", "Manager"]

class IsOwnerOrManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ["Owner", "Manager"]
