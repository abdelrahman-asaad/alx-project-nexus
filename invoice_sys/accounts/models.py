from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

class UserManager(BaseUserManager):  #custom user manager instead of default one
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    # 1. إلغاء حقل الـ username تماماً
    username = None 
    # 2. جعل الإيميل فريد وإلزامي
    email = models.EmailField(unique=True, db_index=True)
    role = models.CharField(max_length=20, choices=[('owner', 'Owner'), ('manager', 'Manager'),
     ('sales', 'Sales')], db_index=True)

    # 3. إخبار دجانغو أن الإيميل هو المعرف الأساسي
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [] # الإيميل والباسورد مطلوبين تلقائياً

    objects = UserManager() # ربط المانجر الجديد
    class Meta:
        # إضافة Index مركب لو كنت هتبحث بالإيميل والـ Role سوا كتير
        indexes = [
            models.Index(fields=['email', 'role']),
        ]
    def save(self, *args, **kwargs):
        # لو اليوزر ده superuser، خليه Owner أوتوماتيك
        if self.is_superuser:
            self.role = 'owner'
        super().save(*args, **kwargs)