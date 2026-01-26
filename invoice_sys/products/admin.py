from django.contrib import admin
from django.utils.html import format_html
from .models import Product, Category

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category_name",
        "original_price",
        "currency",
        "sale_price",
        "stock",
        "colored_stock_status",  # 🔹 تلوين المخزون
        "is_in_stock"
    )

    list_filter = ("category", "currency")
    search_fields = ("name", "description", "category__name")
    readonly_fields = ("sale_price",)
    def save_model(self, request, obj, form, change):
        # لو فيه سعر أصلي وعملة، حوله للجنيه
        if obj.original_price and obj.currency:
            obj.sale_price = Product.convert_price_to_egp(obj.original_price, obj.currency)
        super().save_model(request, obj, form, change) 
    def category_name(self, obj):
        return obj.category.name if obj.category else "-"
    category_name.admin_order_field = "category__name"

    def is_in_stock(self, obj):
        return obj.stock > 0
    is_in_stock.boolean = True
    is_in_stock.short_description = "In Stock"

    def colored_stock_status(self, obj):
        """يعطي لون حسب كمية المخزون"""
        if obj.stock == 0:
            color = "red"
            text = "Out of Stock"
        elif obj.stock < 10:
            color = "orange"
            text = "Low Stock"
        else:
            color = "green"
            text = "In Stock"
        return format_html('<span style="color: {};">{}</span>', color, text)

    colored_stock_status.admin_order_field = "stock"
    colored_stock_status.short_description = "Stock Status"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
