from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from invoices.models import Invoice
from .models import Payment
from clients.models import Client

User = get_user_model()

class PaymentAPITests(APITestCase):
    def setUp(self):
        # 1. تحديث اليوزرز: استخدام الإيميل وتوحيد الأدوار لـ lowercase
        self.manager = User.objects.create_user(email="manager@test.com", password="manager123", role="manager")
        self.accountant = User.objects.create_user(email="accountant@test.com", password="accountant123", role="accountant")
        self.sales = User.objects.create_user(email="sales@test.com", password="sales123", role="sales")

        # إنشاء عميل
        self.client_obj = Client.objects.create(name="Client A", email="client@example.com", company_name="Company A")

        # إنشاء فاتورة (تأكد أن الـ status "unpaid" مسموح بها في الـ choices بموديل Invoice)
        self.invoice = Invoice.objects.create(client=self.client_obj, total_amount=1000, status="unpaid")

        self.url = reverse("payment-list-create") 

    # الوصول غير المصرح به
    def test_access_denied_for_sales(self):
        # تسجيل الدخول بالإيميل
        self.client.login(email="sales@test.com", password="sales123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.client.logout()

    # الوصول المصرح به للمدير والمحاسب
    def test_access_allowed_for_manager_and_accountant(self):
        users_data = [
            ("manager@test.com", "manager123"),
            ("accountant@test.com", "accountant123")
        ]
        for email, password in users_data:
            self.client.login(email=email, password=password)
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.client.logout()

    # إنشاء دفعة جديدة وتحديث حالة الفاتورة
    def test_create_payment_updates_invoice_status(self):
        self.client.login(email="accountant@test.com", password="accountant123")
        data = {
            "invoice": self.invoice.id,
            "amount": 1000,
            "method": "Cash"
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.invoice.refresh_from_db()
        # تأكد أن حالة الفاتورة تتحول لـ "paid" في الـ Signals أو الـ Serializer عندك
        self.assertEqual(self.invoice.status, "paid")
        self.client.logout()