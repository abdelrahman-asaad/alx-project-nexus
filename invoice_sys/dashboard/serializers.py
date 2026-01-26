from rest_framework import serializers
from .models import TotalClients, TotalInvoices

class TotalClientsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TotalClients
        fields = ['id', 'total', 'created_at']

class TotalInvoicesSerializer(serializers.ModelSerializer):
    class Meta:
        model = TotalInvoices
        fields = ['id', 'total', 'created_at']
