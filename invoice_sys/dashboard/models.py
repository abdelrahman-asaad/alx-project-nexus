from django.db import models
from django.conf import settings
from common.models import BaseModel  # لو عايز كل حاجة تورث BaseModel

class Widget(BaseModel):
    WIDGET_TYPES = [
        ('total_clients', 'Total Clients'),
        ('total_invoices', 'Total Invoices'),
        ('total_payments', 'Total Payments'),
        ('recent_activities', 'Recent Activities'),
    ]

    name = models.CharField(max_length=100)
    widget_type = models.CharField(max_length=50, choices=WIDGET_TYPES)
    description = models.TextField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


class DashboardConfig(BaseModel): # to specify dashboard to the user role
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='dashboard_config'
    )
    widgets_order = models.JSONField(default=list)  # لتخزين ترتيب الويدجتس حسب المستخدم

    def __str__(self):
        return f"Dashboard config for {self.user.username}"


# اختياري لو تحب تعمل سجل للأنشطة الأخيرة
class ActivityLog(BaseModel):
    action = models.CharField(max_length=200)
    model_name = models.CharField(max_length=50)
    object_id = models.PositiveIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.action} on {self.model_name}({self.object_id})"
