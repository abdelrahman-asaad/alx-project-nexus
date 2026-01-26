from rest_framework import serializers
from .models import Product

from rest_framework import serializers
from .models import Product

class PublicProductSerializer(serializers.ModelSerializer): #for any user to watch
    class Meta:
        model = Product
        fields = ["id", "name", "description", "sale_price", "currency"]


class FullProductSerializer(serializers.ModelSerializer): #fot manager and owner to watch or create
    class Meta:
        model = Product
        fields = ["id", "name", "description", "sale_price", "cost_price", "currency"]
