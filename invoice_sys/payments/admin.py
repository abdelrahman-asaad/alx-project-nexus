from django.contrib import admin
from .models import Payment

# =========================
# Admin للـ Payments
# =========================
from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "invoice", "amount", "method", "created_at", "user")
    readonly_fields = ("created_at",)
    list_filter = ("method", "created_at", "user")
    search_fields = ("invoice__id", "user__username")


    def invoice_id(self, obj):
        return obj.invoice.id
    invoice_id.admin_order_field = "invoice__id"
    invoice_id.short_description = "Invoice #"
