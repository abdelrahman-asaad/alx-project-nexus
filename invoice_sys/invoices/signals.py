# 📌 signals.py في تطبيق الفواتير
# الهدف: تحديث إجمالي الفاتورة + إدارة المخزون عند إنشاء/تعديل/حذف العناصر

from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from .models import InvoiceItem, Invoice


# ======================================================
# 🟢 تحديث إجمالي الفاتورة (total_amount)
# ======================================================
def update_invoice_total(invoice):
    """إعادة حساب إجمالي الفاتورة من جميع العناصر"""
    total = sum(item.total_price for item in invoice.items.all())  # related_name='items'
    invoice.total_amount = total
    invoice.save()


@receiver(post_save, sender=InvoiceItem)
def update_total_on_save(sender, instance, created, **kwargs):
    """يشتغل لما نضيف أو نعدل عنصر في الفاتورة"""
    update_invoice_total(instance.invoice)


@receiver(post_delete, sender=InvoiceItem)
def update_total_on_delete(sender, instance, **kwargs):
    """يشتغل لما نحذف عنصر من الفاتورة"""
    update_invoice_total(instance.invoice)


# ======================================================
# 🟡 إدارة المخزون (stock)
# ======================================================

@receiver(pre_save, sender=InvoiceItem)
def adjust_stock_on_update(sender, instance, **kwargs):
    """
    عند تعديل عنصر موجود:
    - رجّع الكمية القديمة
    - خصم الكمية الجديدة
    """
    if instance.pk:  # يعني العنصر كان موجود وبيتم تعديله
        old_item = InvoiceItem.objects.get(pk=instance.pk)
        diff = instance.quantity - old_item.quantity  # الفرق بين القديم والجديد
        instance.product.stock -= diff
        instance.product.save()


@receiver(post_save, sender=InvoiceItem)
def reduce_stock_on_create(sender, instance, created, **kwargs):
    """
    عند إضافة عنصر جديد في الفاتورة:
    - خصم الكمية من المخزون
    """
    if created:
        instance.product.stock -= instance.quantity
        instance.product.save()


@receiver(post_delete, sender=InvoiceItem)
def restore_stock_on_delete(sender, instance, **kwargs):
    """
    عند حذف عنصر من الفاتورة:
    - إرجاع الكمية للمخزون
    """
    instance.product.stock += instance.quantity
    instance.product.save()

