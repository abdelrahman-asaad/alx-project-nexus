from rest_framework import serializers
from .models import Payment

class PaymentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    invoice = serializers.StringRelatedField()

    class Meta:
        model = Payment
        fields = ['id', 'invoice', 'amount', 'date', 'user', 'method', 'created_at', 'updated_at']
        read_only_fields = ["id", "user", "created_at", "updated_at"]
