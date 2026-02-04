from django.db import models
from django.conf import settings

class AuditLog(models.Model):
    # تعريف الخيارات المتاحة للأكشن
    ACTION_CHOICES = (
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
    )

    # الحقول الأساسية
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='audit_logs'
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100)
    object_id = models.PositiveIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    changes_summary = models.TextField()

    # تحسينات إضافية لضمان عمل المشروع بشكل احترافي
    class Meta:
        ordering = ['-timestamp']  # الأحدث يظهر أولاً (يحل الـ UnorderedObjectListWarning)
        verbose_name = "Audit Log"
        verbose_name_plural = "Audit Logs"

    def __str__(self):
        # استخدام الإيميل بدلاً من اليوزرنيم في العرض
        return f"{self.user.email} - {self.action} - {self.model_name} (ID: {self.object_id})"