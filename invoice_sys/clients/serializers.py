from rest_framework import serializers
from .models import Client

class ClientSerializer(serializers.ModelSerializer):
    # إظهار إيميل من قام بإنشاء العميل بدلاً من الـ ID
    created_by_email = serializers.ReadOnlyField(source='created_by.email')

    class Meta:
        model = Client
        fields = ["id", "name", "email", "phone", "company_name", "address", "created_by", "created_by_email", "created_at"]
        read_only_fields = ["created_by", "created_at"] # حماية الحقول التلقائية