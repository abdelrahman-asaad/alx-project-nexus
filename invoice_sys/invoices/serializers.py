from rest_framework import serializers
from .models import Invoice, InvoiceItem

class InvoiceItemSerializer(serializers.ModelSerializer):
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = InvoiceItem
        fields = ['id', 'product', 'quantity', 'unit_price', 'total_price']


class InvoiceSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(many=True) #nested serializer field #many to make more than one item to invoice
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Invoice
        fields = ['id', 'client', 'user', 'date', 'due_date', 'status', 'total_amount', 'items']

    def create(self, validated_data): #built-in method
        items_data = validated_data.pop('items') #because items is not original field in Invoice 
        invoice = Invoice.objects.create(**validated_data) #such as client, user ,date ...
        for item_data in items_data:
            InvoiceItem.objects.create(invoice=invoice, **item_data) #invoice + items_data
        invoice.save()  # لحساب total_amount
        return invoice

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None) #if there is no items return none instead of error

        for attr, value in validated_data.items():
            setattr(instance, attr, value)  #attr reffreing tp filed such as client , status ...
            
            #value refferring to value of field assigned in validated_data after resopnse like that :
#  '''validated_data = {
#    "client": <Client object (id=1)>,   # serializer بيحوّل الـ id إلى object
#    "status": "paid",
#    "due_date": datetime.date(2025, 9, 10)
#}
#'''

        if items_data is not None:
            instance.items.all().delete()
            for item_data in items_data:
                InvoiceItem.objects.create(invoice=instance, **item_data)

        instance.save()
        return instance
