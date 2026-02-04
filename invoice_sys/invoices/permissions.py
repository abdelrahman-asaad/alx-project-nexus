from rest_framework.permissions import BasePermission

class IsSalesOrManager(BasePermission):
    def has_permission(self, request, view):
        # تم التغيير لـ lowercase
        return request.user.is_authenticated and request.user.role in ["sales", "manager", "owner"]

class IsManager(BasePermission):
    def has_permission(self, request, view):
        # تم التغيير لـ lowercase (الـ owner عادة له صلاحيات الـ manager أيضاً)
        return request.user.is_authenticated and request.user.role in ["manager", "owner"]

class IsOwner(BasePermission):
    def has_permission(self, request, view):
        # تم التغيير لـ lowercase
        return request.user.is_authenticated and request.user.role == "owner"