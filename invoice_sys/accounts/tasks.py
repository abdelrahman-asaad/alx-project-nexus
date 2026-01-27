# accounts/tasks.py
from celery import shared_task
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.conf import settings # الاستيراد يكون فوق خالص

@shared_task
def notify_owner_user_verified(user_id):
    User = get_user_model()
    try:
        # 1. جلب المستخدم بمرونة (إيميل أو ID)
        if isinstance(user_id, str) and '@' in user_id:
            activated_user = User.objects.get(email=user_id)
        else:
            activated_user = User.objects.get(pk=user_id)
        
        # 2. البحث عن الأونر (السوبر يوزر اللي خليناه أونر)
        owner = User.objects.filter(role='owner').first()
        
        # لو مش لاقي أونر، ابعت للإيميل الأساسي في الإعدادات كـ Backup
        target_email = owner.email if (owner and owner.email) else settings.EMAIL_HOST_USER

        # 3. إرسال الإيميل الفعلي
        send_mail(
            subject='تنبيه: مستخدم جديد أكمل التسجيل',
            message=f'المستخدم صاحب الإيميل {activated_user.email} قام بتفعيل حسابه بنجاح.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[target_email],
            fail_silently=False,
        )
        return f"Email sent to {target_email} regarding {activated_user.email}"

    except User.DoesNotExist:
        return "User not found"
    except Exception as e:
        # عشان لو فيه مشكلة في SMTP تظهر بوضوح في الـ Logs
        return f"Error occurred: {str(e)}"