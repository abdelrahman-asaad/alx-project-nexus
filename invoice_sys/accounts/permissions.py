from rest_framework import permissions

class IsOwner(permissions.BasePermission):#custom permissions creation
    """
    يسمح فقط للـ Owner بالوصول.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "owner"


class IsManager(permissions.BasePermission):
    """
    يسمح فقط للـ Manager بالوصول.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "manager"


class IsSales(permissions.BasePermission):
    """
    يسمح فقط للـ Sales بالوصول.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "sales"


class IsOwnerOrManager(permissions.BasePermission):
    """
    يسمح للـ Owner أو Manager بالوصول.
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated 
            and request.user.role in ["owner", "manager"]
        )
