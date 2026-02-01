from django.db import models
from invoices.models import Invoice
from django.conf import settings
# حذفنا timezone لأن BaseModel هو اللي هيهندل التوقيت
from common.models import BaseModel 

# ✅ الوراثة من BaseModel بتديك (created_at, updated_at, created_by) أوتوماتيك in common/models.py
class Payment(BaseModel): 
    METHOD_CHOICES = (
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('bank', 'Bank Transfer'),
    )

    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments')
    date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="payments")
    
    # ❌ شيلنا سطر created_at من هنا تماماً علشان ميحصلش تعارض مع اللي في BaseModel

    def __str__(self):
        return f"Payment for Invoice #{self.invoice.id}"