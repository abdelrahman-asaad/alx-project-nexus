import json
from django.shortcuts import render
from django.db.models import Sum, Count, F, DecimalField, ExpressionWrapper
from django.db.models.functions import TruncMonth
from django.core.serializers.json import DjangoJSONEncoder

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import BasePermission
from rest_framework import serializers

# --- 🚀 استيراد أدوات التوثيق (Swagger Tools) ---
from drf_spectacular.utils import extend_schema, inline_serializer

from invoices.models import Invoice, InvoiceItem
from payments.models import Payment
from clients.models import Client 

# 🔒 صلاحيات: التحقق من أن المستخدم صاحب العمل أو مدير
class IsOwnerOrManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ["owner", "manager"]


# 📊 Sales Summary View (API)
class SalesSummaryView(APIView):
    permission_classes = [IsOwnerOrManager]

    # 📝 تعريف شكل البيانات للـ Swagger باستخدام inline_serializer
    # لأن الـ APIView لا ترتبط بموديل واحد بشكل مباشر (تستخدم حسابات متغيرة)
    @extend_schema(
        responses={
            200: inline_serializer(
                name='SalesSummaryResponse',
                fields={
                    'total_sales': serializers.DecimalField(max_digits=12, decimal_places=2),
                    'monthly_sales': serializers.ListField(child=serializers.DictField())
                }
            )
        },
        description="عرض ملخص إجمالي المبيعات والمبيعات الشهرية"
    )
    def get(self, request):
        # 1. حساب إجمالي المبيعات
        total_sales = Invoice.objects.aggregate(total=Sum('total_amount'))['total'] or 0

        # 2. المبيعات الشهرية: تجميع الفواتير حسب الشهر
        monthly_sales = (
            Invoice.objects
            .annotate(month=TruncMonth('date')) # تحويل التاريخ لأول يوم في الشهر للتجميع
            .values('month')                   # Group By الشهر
            .annotate(total=Sum('total_amount'))# مجموع مبيعات كل شهر
            .order_by('month')
        )

        data = {
            "total_sales": total_sales,
            "monthly_sales": [
                {
                    "month_year": item['month'].strftime("%B %Y") if item['month'] else "Unknown", 
                    "total": item['total']
                }
                for item in monthly_sales
            ]
        }
        return Response(data)


# 💰 Profit Tracker View (API)
class ProfitTrackerView(APIView):
    permission_classes = [IsOwnerOrManager]

    @extend_schema(
        responses={
            200: inline_serializer(
                name='ProfitTrackerResponse',
                fields={
                    'profit_tracker': serializers.ListField(child=serializers.DictField())
                }
            )
        },
        description="تتبع صافي الأرباح شهرياً (سعر البيع - التكلفة)"
    )
    def get(self, request):
        # حساب الربح لكل بند: (سعر الوحدة - تكلفة المنتج) * الكمية
        profit_data = (
            InvoiceItem.objects
            .annotate(
                month=TruncMonth('invoice__date'),
                profit=ExpressionWrapper(
                    (F('unit_price') - F('product__cost_price')) * F('quantity'),
                    output_field=DecimalField(max_digits=10, decimal_places=2)
                )
            )
            .values('month')
            .annotate(total_profit=Sum('profit'))
            .order_by('month')
        )

        data = {
            "profit_tracker": [
                {
                    "month_year": item['month'].strftime("%B %Y") if item['month'] else "Unknown",
                    "profit": item['total_profit']
                }
                for item in profit_data
            ]
        }
        return Response(data)


# 🏠 Dashboard Page (Template View)
# هذه الدالة مخصصة لعرض صفحة الـ HTML (Frontend) وليس للـ API
def dashboard_page(request):
    # 🟦 KPIs: المؤشرات الرئيسية
    total_sales = Invoice.objects.aggregate(total=Sum('total_amount'))['total'] or 0
    total_paid = Payment.objects.aggregate(total=Sum('amount'))['total'] or 0
    active_clients = Client.objects.aggregate(total=Count('id'))['total'] or 0

    # 💰 حساب الأرباح الكلية والبيانات الشهرية للـ Charts
    profit_data = (
        InvoiceItem.objects
        .annotate(
            month=TruncMonth('invoice__date'),
            profit=ExpressionWrapper(
                (F('unit_price') - F('product__cost_price')) * F('quantity'),
                output_field=DecimalField(max_digits=10, decimal_places=2)
            )
        )
        .values('month')
        .annotate(total_profit=Sum('profit'))
        .order_by('month')
    )

    total_profit = sum(item["total_profit"] or 0 for item in profit_data)

    # 📊 مبيعات شهرية للـ Charts
    monthly_sales = (
        Invoice.objects
        .annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(total=Sum('total_amount'))
        .order_by('month')
    )

    # 🟦 تحويل البيانات لـ JSON عشان الـ JavaScript (Charts.js مثلاً) يقدر يقرأها
    sales_json = json.dumps(
        [{"month": item['month'].strftime("%B %Y"), "total": float(item['total'])} for item in monthly_sales if item['month']],
        cls=DjangoJSONEncoder
    )

    profit_json = json.dumps(
        [{"month": item['month'].strftime("%B %Y"), "profit": float(item['total_profit'])} for item in profit_data if item['month']],
        cls=DjangoJSONEncoder
    )

    context = {
        "total_sales": total_sales,
        "total_profit": total_profit,
        "active_clients": active_clients,
        "sales_data": sales_json,
        "profit_data": profit_json,
    }
    return render(request, "dashboard/dashboard.html", context)