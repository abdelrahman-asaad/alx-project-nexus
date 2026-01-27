from django.db import models
from django.conf import settings


#  اختيارات العملات
CURRENCY_CHOICES = [
    ("USD", "US Dollar"),
    ("EUR", "Euro"),
    ("EGP", "Egyptian Pound"),
]

#  أسعار الصرف (افتراضي للتجربة - ممكن تربطه بـ API خارجي)
CURRENCY_RATES = {
    "USD": 48,   # مثال: 1 USD = 48 EGP
    "EUR": 52,   # مثال: 1 EUR = 52 EGP
    "EGP": 1,
}


class Category(models.Model):
    
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    
#class StockHistory(models.Model):
#    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='stock_history')
#    old_stock = models.IntegerField()
#    new_stock = models.IntegerField()
#    changed_at = models.DateTimeField(auto_now_add=True)
#    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)    


class Product(models.Model):
    name = models.CharField(max_length=100, unique=True) #send to json
    description = models.TextField(blank=True, null=True) #null > dont send to json

    #  السعر بعد التحويل للجنيه (اللي هنتعامل بيه في النظام)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2) #send to json
    cost_price = models.DecimalField(max_digits=10, decimal_places=2) #send to json

    # السعر الأصلي + عملته
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True) #dont send to json
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default="EGP")
#blank و null مش متعرفة → الافتراض:
#blank=False → الـ serializer هيتطلب الحقل.
#null=False → الـ DB ما يسمحش بقيمة NULL.
#عندك default="EGP" → لو مابعتش الحقل، Django هيخزن "EGP" تلقائيًا.
    
    category = models.ForeignKey("Category", on_delete=models.SET_NULL, null=True, blank=True) #dont send to json
    stock = models.PositiveIntegerField(default=0)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="products_created")
    def __str__(self):
        return f"{self.name} ({self.sale_price} EGP)"


    #  تحويل أي سعر إلى الجنيه
    @staticmethod 
    def convert_price_to_egp(amount, currency):
        rate = CURRENCY_RATES.get(currency, 1) # one EGP if currency not found
        return amount * rate

    #  تسجيل حركة المخزون
    def track_stock(self, old_stock, new_stock):
        StockHistory.objects.create(product=self, old_stock=old_stock, new_stock=new_stock)

    #  تقليل المخزون بعد عملية بيع
    def reduce_stock(self, quantity):
        if quantity > self.stock:
            raise ValueError("Not enough stock available")
        old_stock = self.stock
        self.stock -= quantity
        self.save(update_fields=["stock"])
        self.track_stock(old_stock, self.stock)

    #  زيادة المخزون (مثلاً عند إلغاء فاتورة)
    def increase_stock(self, quantity):
        old_stock = self.stock
        self.stock += quantity
        self.save(update_fields=["stock"])
        self.track_stock(old_stock, self.stock)


class StockHistory(models.Model):
    """تاريخ تغييرات المخزون لكل منتج"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="stock_history")
    old_stock = models.PositiveIntegerField()
    new_stock = models.PositiveIntegerField()
    changed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name}: {self.old_stock} → {self.new_stock}"
