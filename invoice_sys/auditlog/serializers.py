from rest_framework import serializers
from .models import AuditLog

class AuditLogSerializer(serializers.ModelSerializer):
    # إظهار إيميل المستخدم بدلاً من الـ ID فقط لسهولة القراءة
    user_email = serializers.ReadOnlyField(source='user.email')

    class Meta:
        model = AuditLog
        fields = ['id', 'user', 'user_email', 'action', 'model_name', 'object_id', 'timestamp', 'changes_summary']