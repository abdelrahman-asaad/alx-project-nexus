from django.db import models
from django.conf import settings

class AuditLog(models.Model):
    ACTION_CHOICES = (
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100)
    object_id = models.PositiveIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    changes_summary = models.TextField()

    def __str__(self):
        return f"{self.action} - {self.model_name} (ID: {self.object_id})"
