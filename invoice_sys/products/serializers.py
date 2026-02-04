from rest_framework import serializers
from .models import Product

from rest_framework import serializers
from .models import Product

class PublicProductSerializer(serializers.ModelSerializer): #for any user to watch
    class Meta:
        model = Product
        fields = ["id", "name", "description", "sale_price", "currency"]
        read_only_fields = ["id", "created_at"]
    def validate(self, data):
        # التأكد إن سعر البيع أكبر من التكلفة
        if data['sale_price'] < data['cost_price']:
            raise serializers.ValidationError("Sale price cannot be lower than cost price!")
        return data

class FullProductSerializer(serializers.ModelSerializer): #fot manager and owner to watch or create
    class Meta:
        model = Product
        fields = ["id", "name", "description", "sale_price", "cost_price", "currency"]
