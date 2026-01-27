from rest_framework import serializers
from .models import Client

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields =  ["name", "email", "phone", "company_name", "address", "created_by", "created_at"]