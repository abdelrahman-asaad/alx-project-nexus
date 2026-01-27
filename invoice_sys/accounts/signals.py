from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User
from .tasks import notify_owner_user_verified

@receiver(post_save, sender=User)
def trigger_owner_notification(sender, instance, created, **kwargs):
    # إحنا اتفقنا: لو مش جديد (Update) وبقى Active
    if not created and instance.is_active:
        # بنرمي المهمة للـ Celery ونبعت الـ ID بس
        notify_owner_user_verified.delay(instance.pk)