from rest_framework.permissions import BasePermission

class IsAccountantOrManager(BasePermission):
    def has_permission(self, request, view):
        # التعديل لـ lowercase وإضافة الـ owner للصلاحية
        return request.user.is_authenticated and request.user.role in ["accountant", "manager", "owner"]