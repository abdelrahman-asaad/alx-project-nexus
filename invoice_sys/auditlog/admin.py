from django.contrib import admin
from .models import AuditLog

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    # 1. تحديث قائمة العرض (الإيميل سيظهر تلقائياً مكان اليوزر)
    list_display = ("id", "user", "action", "model_name", "object_id", "timestamp")
    
    # 2. الفلاتر الجانبية
    list_filter = ("action", "model_name", "timestamp")
    
    # 3. تعديل حقل البحث (تغيير username إلى email) - "مهم جداً"
    search_fields = ("user__email", "model_name", "object_id", "changes_summary")
    
    # 4. جعل الحقول للقراءة فقط (لأن سجلات الرقابة لا يجب تعديلها يدوياً)
    readonly_fields = ("action", "user", "model_name", "object_id", "timestamp", "changes_summary")

    # تحسين اختياري: إضافة ترتيب افتراضي في الـ Admin
    ordering = ("-timestamp",)