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
        # إنشاء مستخدمين
        self.manager = User.objects.create_user(username="manager", password="manager123", role="Manager")
        self.accountant = User.objects.create_user(username="accountant", password="accountant123", role="Accountant")
        self.sales = User.objects.create_user(username="sales", password="sales123", role="Sales")

        # إنشاء عميل
        self.client_obj = Client.objects.create(name="Client A", email="client@example.com", company_name="Company A")

        # إنشاء فاتورة
        self.invoice = Invoice.objects.create(client=self.client_obj, total_amount=1000, status="unpaid")

        self.url = reverse("payment-list-create") 

    # الوصول غير المصرح به
    def test_access_denied_for_sales(self):
        self.client.login(username="sales", password="sales123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.client.logout()

    # الوصول المصرح به للمدير والمحاسب
    def test_access_allowed_for_manager_and_accountant(self):
        for user in [self.manager, self.accountant]:
            self.client.login(username=user.username, password=f"{user.username}123")
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.client.logout()

    # إنشاء دفعة جديدة وتحديث حالة الفاتورة
    def test_create_payment_updates_invoice_status(self):
        self.client.login(username="accountant", password="accountant123")
        data = {
            "invoice": self.invoice.id,
            "amount": 1000,
            "method": "Cash"
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.invoice.refresh_from_db()
        self.assertEqual(self.invoice.status, "paid")  # تأكد إن حالة الفاتورة اتحدثت
        self.client.logout()
