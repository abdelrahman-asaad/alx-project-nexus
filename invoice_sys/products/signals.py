from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver

# 🔹 استيراد النماذج داخل الدوال لتجنب circular import
from invoices.models import InvoiceItem, Invoice
from .models import StockHistory



# ======================================================
# 🔹 تحديث إجمالي الفاتورة (total_amount)
# ======================================================
def update_invoice_total(invoice): #invoice is any name referring to object from Invoice class
    """
    🔹 إعادة حساب إجمالي الفاتورة من جميع العناصر المرتبطة بها.
    """
    total = sum(item.total_price for item in invoice.items.all())  # related_name='items'
    invoice.total_amount = total                   
    invoice.save(update_fields=["total_amount"])   


@receiver(post_save, sender=InvoiceItem) #once POST
def update_total_on_save(sender, instance, created, **kwargs):
    """يشتغل عند إضافة أو تعديل عنصر في الفاتورة"""
    update_invoice_total(instance.invoice) #instance is object of InvoiceItem and .invoice is the forignkey


@receiver(post_delete, sender=InvoiceItem) 
def update_total_on_delete(sender, instance, **kwargs):
    """يشتغل عند حذف عنصر من الفاتورة"""
    update_invoice_total(instance.invoice)


# ======================================================
# 🔹 إدارة المخزون + تسجيل StockHistory
# ======================================================
@receiver(pre_save, sender=InvoiceItem)
def adjust_stock_on_update(sender, instance, **kwargs):
    """
    🔹 عند تعديل عنصر موجود:
    - إعادة المخزون القديم
    - خصم الكمية الجديدة
    """
    if instance.pk:  # العنصر موجود بالفعل
        old_item = InvoiceItem.objects.get(pk=instance.pk)
        product = instance.product

        # 🔹 إعادة المخزون القديم
        product.increase_stock(old_item.quantity)

        # 🔹 خصم المخزون الجديد
        product.reduce_stock(instance.quantity)

        # 🔹 تسجيل التاريخ
        StockHistory.objects.create(
            product=product,
            old_stock=product.stock + instance.quantity,  # قبل التغيير
            new_stock=product.stock                       # بعد التغيير
        )


@receiver(post_save, sender=InvoiceItem)
def reduce_stock_on_create(sender, instance, created, **kwargs):
    """
    🔹 عند إنشاء عنصر جديد:
    - خصم المخزون
    - تسجيل StockHistory
    """
    if created:
        product = instance.product
        product.reduce_stock(instance.quantity)

        StockHistory.objects.create(
            product=product,
            old_stock=product.stock + instance.quantity,  # قبل الخصم
            new_stock=product.stock                       # بعد الخصم
        )


@receiver(post_delete, sender=InvoiceItem)
def restore_stock_on_delete(sender, instance, **kwargs):
    """
    🔹 عند حذف عنصر من الفاتورة:
    - إعادة المخزون
    - تسجيل StockHistory
    """
    product = instance.product
    product.increase_stock(instance.quantity)

    StockHistory.objects.create(
        product=product,
        old_stock=product.stock - instance.quantity,  # قبل الإضافة
        new_stock=product.stock                       # بعد الإضافة
    )

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Product

@receiver([post_save, post_delete], sender=Product)
def clear_product_cache(sender, instance, **kwargs):
    # بنمسح كاش الـ Redis أول ما منتج يتضاف أو يتمسح أو يتعدل
    # ملحوظة: cache_page بتستخدم URL كـ key، فإحنا ممكن نمسح الكاش كله ببساطة
    cache.clear()     #clears all cache of Redis that also includes products api cache and rate limiting cache
    print("Product cache cleared!")