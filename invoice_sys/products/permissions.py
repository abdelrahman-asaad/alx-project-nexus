from rest_framework import permissions

class IsManagerOrOwner(permissions.BasePermission):
    """
    Allow only Manager or Owner
    """
def has_permission(self, request, view):
    return (
        request.user.is_authenticated
        and request.user.role.lower() in ["manager", "owner"]
    )
