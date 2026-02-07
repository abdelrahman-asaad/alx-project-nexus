import graphene
from graphene_django import DjangoObjectType
from django.db.models import Sum, Count
from decimal import Decimal

# استيراد الموديلات من الـ Apps التانية
from invoices.models import Invoice
from products.models import Product
# استيراد الـ Type بتاع الفاتورة (مهم جداً لخطوة الـ latest_invoices)
from invoices.schema import InvoiceType 

class DashboardStatsType(graphene.ObjectType):
    total_revenue = graphene.Decimal()
    total_invoices_count = graphene.Int()
    pending_invoices_count = graphene.Int()

class DashboardQuery(graphene.ObjectType): # غيرنا الاسم لـ DashboardQuery ليكون أوضح
    dashboard_stats = graphene.Field(DashboardStatsType)
    latest_invoices = graphene.List(InvoiceType)
def resolve_dashboard_stats(root, info):
        total_rev = Invoice.objects.filter(status='paid').aggregate(Sum('total_amount'))['total_amount__sum']
        
        # التأكد من إرجاع Decimal حتى لو القيمة None أو 0
        if total_rev is None:
            total_rev = Decimal("0.00")
        else:
            total_rev = Decimal(total_rev)
            
        total_count = Invoice.objects.count()
        pending_count = Invoice.objects.filter(status='unpaid').count()
        
        return DashboardStatsType(
            total_revenue=total_rev,
            total_invoices_count=total_count,
            pending_invoices_count=pending_count
        )

'''query GetFullDashboard {
  # 1. المربعات اللي فوق (Stats)
  dashboardStats {
    totalRevenue
    totalInvoicesCount
    pendingInvoicesCount
  }'''