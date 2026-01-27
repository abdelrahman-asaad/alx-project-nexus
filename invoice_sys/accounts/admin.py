from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

# 1. الفورم الخاص بالإضافة
class UserCreationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('email', 'role', 'is_staff', 'is_active')

    def save(self, commit=True):
        user = super().save(commit=False)
        # جعل الباسورد غير قابل للاستخدام حتى يتم التفعيل
        user.set_unusable_password() 
        if commit:
            user.save()
        return user

# 2. تخصيص لوحة التحكم
class CustomUserAdmin(UserAdmin):
    # نربط الفورم اللي عملناه فوق هنا
    add_form = UserCreationForm  
    
    ordering = ('email',)
    list_display = ('email', 'role', 'is_active')
    
    # حقول صفحة التعديل
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser')}),
    )
    
    # حقول صفحة الإضافة (تأكد أنها نفس حقول الفورم)
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'role', 'is_active', 'is_staff'),
        }),
    )

# 3. تسجيل الموديل
admin.site.register(User, CustomUserAdmin)