from rest_framework.permissions import BasePermission

class IsSalesOrManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ["Sales", "Manager"]

class IsManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "Manager"

class IsOwner(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "Owner"
