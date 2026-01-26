from django.contrib import admin
from .models import Invoice, InvoiceItem, Client, Product
from django.utils.html import format_html

# ===============================
# InvoiceItem Inline داخل Invoice
# ===============================
class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 0
    readonly_fields = ("total_price",)
    autocomplete_fields = ("product",)  # يسهل اختيار المنتجات
    fields = ("product", "quantity", "unit_price", "total_price")

# ===============================
# Invoice Admin
# ===============================
@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("id", "client", "total_amount", "date", "status")
    readonly_fields = ("total_amount",)  # لا تعديل إجمالي الفاتورة
    list_filter = ("status", "date")
    search_fields = ("id", "client__name")

    def has_change_permission(self, request, obj=None):
        # منع التعديل من الـ Admin
        return False

    def has_delete_permission(self, request, obj=None):
        # منع الحذف من الـ Admin
        return False
    def client_name(self, obj):
        return obj.client.name
    client_name.admin_order_field = "client__name"

    def total_amount_colored(self, obj):
        """
        يلوّن إجمالي الفاتورة:
        - >5000 أخضر
        - 1000-5000 برتقالي
        - <1000 أحمر
        """
        total = obj.total_amount
        if total >= 5000:
            color = "green"
        elif total >= 1000:
            color = "orange"
        else:
            color = "red"
        return format_html('<span style="color:{};">{}</span>', color, total)

    total_amount_colored.admin_order_field = "total_amount"
    total_amount_colored.short_description = "Total Amount"

# ===============================
# Client Admin
# ===============================
@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "company_name", "phone")
    search_fields = ("name", "email", "company_name")
