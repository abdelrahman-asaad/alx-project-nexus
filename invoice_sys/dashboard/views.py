from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from django.db.models.functions import TruncMonth
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import BasePermission

from invoices.models import Invoice, InvoiceItem


# 🔒 صلاحيات
class IsOwnerOrManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ["Owner", "Manager"]


# 📊 Sales Summary View
class SalesSummaryView(APIView):
    permission_classes = [IsOwnerOrManager]

    def get(self, request):
        # إجمالي المبيعات
        total_sales = Invoice.objects.aggregate(total=Sum('total_amount'))['total'] or 0

        # المبيعات الشهرية
        monthly_sales = (
            Invoice.objects
            .annotate(month=TruncMonth('date')) #to create month column
            .values('month') #group by month
            .annotate(total=Sum('total_amount')) #to create total column
            .order_by('month')

        )
#[
#    {"month": datetime.date(2025, 7, 1), "total": Decimal("6000.00")},
#    {"month": datetime.date(2025, 8, 1), "total": Decimal("12000.00")},
#    {"month": datetime.date(2025, 9, 1), "total": Decimal("18000.00")}
#]




        data = {
            "total_sales": total_sales,
            "monthly_sales": [
                {"month_year": item['month'].strftime("%B %Y"), "total": item['total']}
                for item in monthly_sales
            ]
        }
        return Response(data)
#{
#  "total_sales": 18000,
#  "monthly_sales": [
#    {"month_year": "July 2025", "total": 6000},
#    {"month_year": "August 2025", "total": 12000}
#  ]
#}
    




# 💰 Profit Tracker View
# Profit Tracker - تجميع شهري
class ProfitTrackerView(APIView):
    permission_classes = [IsOwnerOrManager]
    

    def get(self, request):
        #from invoices.models import InvoiceItem
        # حساب الربح لكل بند
        profit_data = (
            InvoiceItem.objects
            .annotate(
                month=TruncMonth('invoice__date'),  # group by الشهر
                profit=ExpressionWrapper(
                    (F('unit_price') - F('product__cost_price')) * F('quantity'),
                    output_field=DecimalField(max_digits=10, decimal_places=2)
                )
            )
            .values('month')  # تجميع حسب الشهر #group by
            .annotate(total_profit=Sum('profit'))
            .order_by('month')
        )
#        [
#    {"month": datetime.date(2025, 7, 1), "total_profit": Decimal("2000.00")},
#    {"month": datetime.date(2025, 8, 1), "total_profit": Decimal("2480.50")},
#    {"month": datetime.date(2025, 9, 1), "total_profit": Decimal("3150.00")}
#]


       
       
        # تجهيز البيانات للـ JSON
        data = {
            "profit_tracker": [
                {
                    "month_year": item['month'].strftime("%B %Y"),
                    "profit": item['total_profit']
                }
                for item in profit_data
            ]
        }
        return Response(data)
    #{
  #"profit_tracker": [
  #  {"month_year": "July 2025", "profit": "1200.00"},
  #  {"month_year": "August 2025", "profit": "980.50"}
  #]
#}

'''
أن TruncMonth('date') مش بياخد أول فاتورة في الشهر بس، ده بيحوّل كل تاريخ لأي يوم في الشهر إلى تمثيل واحد ثابت للشهر (عادة أول يوم من الشهر)، وده بيخلي كل الفواتير اللي في نفس الشهر تعتبر في نفس المجموعة عند التجميع.

مثال توضيحي:

لو عندك فواتير في أغسطس:

date	total_amount
2025-08-01	100
2025-08-05	200
2025-08-20	150

لو عملت:

Invoice.objects.annotate(month=TruncMonth('date')).values('month').annotate(total=Sum('total_amount'))


الناتج هيبقى:

[
    {"month": datetime.date(2025, 8, 1), "total": 450}  # مجموع كل الفواتير في أغسطس
]


كل الفواتير في أغسطس اتجمعت في صف واحد بالرغم من اختلاف الأيام.

month هنا مجرد تمثيل للشهر مش التاريخ الفعلي لأي فاتورة معينة.'''
from django.shortcuts import render
from django.db.models import Sum, Count, F, DecimalField, ExpressionWrapper
from django.db.models.functions import TruncMonth
from invoices.models import Invoice, InvoiceItem
from payments.models import Payment
from clients.models import Client   # لو اسم الموديل مختلف عدله

import json
from django.core.serializers.json import DjangoJSONEncoder

def dashboard_page(request):
    # 🟦 KPIs
    total_sales = Invoice.objects.aggregate(total=Sum('total_amount'))['total'] or 0
    total_paid = Payment.objects.aggregate(total=Sum('amount'))['total'] or 0
    active_clients = Client.objects.aggregate(total=Count('id'))['total'] or 0

    # 💰 نعتبر الربح = مجموع (سعر البيع - سعر التكلفة) * الكمية
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

    # 📊 مبيعات شهرية
    monthly_sales = (
        Invoice.objects
        .annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(total=Sum('total_amount'))
        .order_by('month')
    )

    # 🟦 تحويل ل JSON للـ Charts
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
    return render(request, "dashboard.html", context)
