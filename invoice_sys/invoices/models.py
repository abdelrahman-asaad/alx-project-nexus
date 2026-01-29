from django.db import models
from common.models import BaseModel
from clients.models import Client
from products.models import Product
from django.conf import settings

class Invoice(BaseModel):
    STATUS_CHOICES = (
        ('paid', 'Paid'),
        ('unpaid', 'Unpaid'),
        ('overdue', 'Overdue'),
    )

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='invoices')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='invoices')
    date = models.DateField(db_index=True)  # إضافة Indexing للتواريخ والحالة
    due_date = models.DateField(db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unpaid', db_index=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, db_index=True)

    class Meta:
        # Index مركب للبحث عن فواتير عميل معين في تاريخ معين (استعلام تقارير مشهور)
        indexes = [
            models.Index(fields=['client', 'date']),
            models.Index(fields=['status', 'date']),
        ]
        ordering = ['-date', '-id']

    def calculate_total(self):
        # استخدام aggregate أسرع بكتير من sum(item.total_price for item in ...)
        from django.db.models import Sum, F
        result = self.items.aggregate(
            total=Sum(F('quantity') * F('unit_price'))
        )
        return result['total'] or 0 
    
    #aggregate is used to perform calculations on a set of values and return a single value.
    #instead of calculating in python we do it in database which is faster with "aggregate" 

#the old method that make query in all items and sum it in python then return the sum is :
#sum(item.total_price for item in self.items.all()) which is slower because it fetches all items and process them in python


    def save(self, *args, **kwargs):
        # لاحظ: الإجمالي بيتحسب بناءً على أصناف موجودة فعلاً في الـ DB
        # لو دي فاتورة جديدة، لازم الأصناف تتسيف الأول
        super().save(*args, **kwargs)
#self is used to refer to the current instance of the model.
    def __str__(self):
        return f"Invoice #{self.id} - {self.client.name}"


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        # Index لسرعة جلب أصناف فاتورة معينة (دجانغو بيعمله للـ FK بس تأكيد)
        indexes = [
            models.Index(fields=['invoice', 'product']),
        ]

    @property
    def total_price(self):
        return self.quantity * self.unit_price

    def __str__(self):
        return f"{self.quantity} x {self.product.name} for Invoice #{self.invoice.id}"
