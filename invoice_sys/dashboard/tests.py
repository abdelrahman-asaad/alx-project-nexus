from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from invoices.models import Invoice, InvoiceItem
from products.models import Product 
from clients.models import Client
from datetime import date

User = get_user_model()

# الكلاس لازم يبدأ بكلمة Test
class DashboardAPITests(APITestCase):

    def setUp(self):
        # إنشاء المدير
        self.manager = User.objects.create_user(
            email="manager@dashboard.com", 
            password="password123", 
            role="manager"
        )
        
        # إنشاء المنتج بالحقول اللي شفناها في الموديل عندك
        self.product = Product.objects.create(
            name="Test Laptop",
            sale_price=1000.00,
            cost_price=500.00,
            stock=10
        )

        # إنشاء العميل
        self.client_obj = Client.objects.create(
            name="Dash Client",
            company_name="Dash Co",
            created_by=self.manager
        )

        # الروابط (تأكد إنها نفس اللي في urls.py)
        self.sales_url = reverse("sales-summary")
        self.profit_url = reverse("profit-tracker")

    # الدوال لازم تبدأ بـ test_
    def test_sales_summary_access(self):
        self.client.force_authenticate(user=self.manager)
        response = self.client.get(self.sales_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_profit_tracker_access(self):
        self.client.force_authenticate(user=self.manager)
        response = self.client.get(self.profit_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)