from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.utils.timezone import now

from .models import AuditLog  # الموديل اللي بيخزن اللوجات
from invoices.models import Invoice  # مثال: بنسجل التغييرات اللي بتحصل على الفواتير


# 🟢 لما يحصل إضافة أو تعديل في Invoice
@receiver(post_save, sender=Invoice)
def log_invoice_save(sender, instance, created, **kwargs):
    """
    يسجل عملية إضافة أو تعديل على الفواتير.
    """
    action = "Created" if created else "Updated"

    AuditLog.objects.create(
        user=getattr(instance, "user", None),   # لو الموديل فيه user بيربط العملية بالمستخدم
        action=action,
        model_name=sender.__name__,
        object_id=instance.id,
        changes=f"Invoice {instance.id} {action.lower()} at {now()}",
        timestamp=now(),
    )


# 🔴 لما يحصل حذف في Invoice
@receiver(post_delete, sender=Invoice)
def log_invoice_delete(sender, instance, **kwargs):
    """
    يسجل عملية حذف على الفواتير.
    """
    AuditLog.objects.create(
        user=getattr(instance, "user", None),
        action="Deleted",
        model_name=sender.__name__,
        object_id=instance.id,
        changes=f"Invoice {instance.id} deleted at {now()}",
        timestamp=now(),
    )

