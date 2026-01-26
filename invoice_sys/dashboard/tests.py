from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from invoices.models import Invoice, InvoiceItem
from products.models import Product

User = get_user_model()

class DashboardAPITests(APITestCase):
    def setUp(self):
        # إنشاء مستخدمين
        self.owner = User.objects.create_user(username="owner", password="owner123", role="Owner")
        self.manager = User.objects.create_user(username="manager", password="manager123", role="Manager")
        self.sales = User.objects.create_user(username="sales", password="sales123", role="Sales")

        # إنشاء منتجات
        self.product1 = Product.objects.create(name="Prod1", cost_price=50, price=100)
        self.product2 = Product.objects.create(name="Prod2", cost_price=30, price=70)

        # إنشاء فواتير وعناصر
        self.invoice1 = Invoice.objects.create(total_amount=0)
        InvoiceItem.objects.create(invoice=self.invoice1, product=self.product1, quantity=2, unit_price=100)
        InvoiceItem.objects.create(invoice=self.invoice1, product=self.product2, quantity=3, unit_price=70)

        # تحديث إجمالي الفاتورة
        self.invoice1.total_amount = sum(item.unit_price * item.quantity for item in self.invoice1.items.all())
        self.invoice1.save()

    # اختبار صلاحية الوصول للـ SalesSummaryView
    def test_sales_summary_access(self):
        url = reverse("sales-summary")
        
        # Owner
        self.client.login(username="owner", password="owner123")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("total_sales", response.data)
        self.client.logout()

        # Manager
        self.client.login(username="manager", password="manager123")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.logout()

        # Sales (غير مسموح)
        self.client.login(username="sales", password="sales123")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.client.logout()

    # اختبار صلاحية الوصول للـ ProfitTrackerView
    def test_profit_tracker_access(self):
        url = reverse("profit-tracker")

        # Owner
        self.client.login(username="owner", password="owner123")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("profit_tracker", response.data)
        self.client.logout()

        # Manager
        self.client.login(username="manager", password="manager123")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.logout()

        # Sales (غير مسموح)
        self.client.login(username="sales", password="sales123")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.client.logout()
