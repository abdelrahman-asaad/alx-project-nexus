from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from invoices.models import Invoice, InvoiceItem
from products.models import Product

User = get_user_model()

class DashboardAPITests(APITestCase):
    def setUp(self):
        # 1. التعديل لاستخدام email وتوحيد الأدوار لـ lowercase
        self.owner = User.objects.create_user(email="owner@test.com", password="owner123", role="owner")
        self.manager = User.objects.create_user(email="manager@test.com", password="manager123", role="manager")
        self.sales = User.objects.create_user(email="sales@test.com", password="sales123", role="sales")

        # إنشاء منتجات
        self.product1 = Product.objects.create(name="Prod1", cost_price=50, price=100)
        self.product2 = Product.objects.create(name="Prod2", cost_price=30, price=70)

        # إنشاء فواتير وعناصر
        # ملاحظة: تأكد أن موديل Invoice لا يتطلب حقولاً إضافية في الـ create
        self.invoice1 = Invoice.objects.create(total_amount=0)
        InvoiceItem.objects.create(invoice=self.invoice1, product=self.product1, quantity=2, unit_price=100)
        InvoiceItem.objects.create(invoice=self.invoice1, product=self.product2, quantity=3, unit_price=70)

        # تحديث إجمالي الفاتورة
        self.invoice1.total_amount = sum(item.unit_price * item.quantity for item in self.invoice1.items.all())
        self.invoice1.save()

    # اختبار صلاحية الوصول للـ SalesSummaryView
    def test_sales_summary_access(self):
        url = reverse("sales-summary")
        
        # Owner - استخدام email في الـ login
        self.client.login(email="owner@test.com", password="owner123")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # التأكد من وجود البيانات المطلوبة في الـ response
        self.client.logout()

        # Manager
        self.client.login(email="manager@test.com", password="manager123")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.logout()

        # Sales (غير مسموح له بالدخول لملخص المبيعات الشامل حسب الـ logic)
        self.client.login(email="sales@test.com", password="sales123")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.client.logout()

    # اختبار صلاحية الوصول للـ ProfitTrackerView
    def test_profit_tracker_access(self):
        url = reverse("profit-tracker")

        # Owner
        self.client.login(email="owner@test.com", password="owner123")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.logout()

        # Manager
        self.client.login(email="manager@test.com", password="manager123")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.logout()

        # Sales (غير مسموح)
        self.client.login(email="sales@test.com", password="sales123")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.client.logout()