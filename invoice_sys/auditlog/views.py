from rest_framework import generics, permissions, filters
from .models import AuditLog
from .serializers import AuditLogSerializer
from django_filters.rest_framework import DjangoFilterBackend

class IsAdminOrOwner(permissions.BasePermission):
    
    def has_permission(self, request, view):
        return request.user and (request.user.is_superuser or request.user.is_staff)

class AuditLogListView(generics.ListAPIView):
    queryset = AuditLog.objects.all().order_by("-timestamp")
    serializer_class = AuditLogSerializer
    permission_classes = [IsAdminOrOwner]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    # الفلاتر اللي ممكن المستخدم يستخدمها
    filterset_fields = ["user", "action"]

    # البحث في هذه الحقول
    search_fields = ['user__email', 'model_name', 'action', 'changes_summary']

    # ترتيب حسب timestamp أو user
    ordering_fields = ["timestamp", "user__username"]
    ordering = ["-timestamp"]  # ترتيب افتراضي