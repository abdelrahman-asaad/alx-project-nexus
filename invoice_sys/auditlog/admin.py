from django.contrib import admin
from .models import AuditLog

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("id", "action", "user", "model_name", "object_id", "timestamp")
    list_filter = ("action", "model_name", "timestamp")
    search_fields = ("user__username", "model_name", "object_id")
    readonly_fields = ("action", "user", "model_name", "object_id", "timestamp")