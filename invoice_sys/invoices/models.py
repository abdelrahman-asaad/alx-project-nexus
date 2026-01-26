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
    date = models.DateField()
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unpaid')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def calculate_total(self):
        return sum(item.total_price for item in self.items.all())

    def save(self, *args, **kwargs):
        self.total_amount = self.calculate_total()
        super().save(*args, **kwargs)
#self is used to refer to the current instance of the model.
    def __str__(self):
        return f"Invoice #{self.id} - {self.client.name}"


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def total_price(self):
        return self.quantity * self.unit_price

    def __str__(self):
        return f"{self.quantity} x {self.product.name} for Invoice #{self.invoice.id}"
