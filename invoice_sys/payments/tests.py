from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from invoices.models import Invoice
from .models import Payment
from clients.models import Client
from datetime import date, timedelta

User = get_user_model()

class PaymentAPITests(APITestCase):
    def setUp(self):
        # 1. اليوزرز (lowercase roles)
        self.manager = User.objects.create_user(email="manager@test.com", password="manager123", role="manager")
        self.accountant = User.objects.create_user(email="accountant@test.com", password="accountant123", role="accountant")
        self.sales = User.objects.create_user(email="sales@test.com", password="sales123", role="sales")

        # 2. عميل وفاتورة (تأكد من الحقول الإلزامية للفاتورة)
        self.client_obj = Client.objects.create(name="Client A", company_name="Company A", created_by=self.manager)
        
        self.invoice = Invoice.objects.create(
            client=self.client_obj, 
            total_amount=1000, 
            status="unpaid",
            user=self.manager, # الحقل اللي اكتشفناه في الفواتير
            date=date.today(),
            due_date=date.today() + timedelta(days=7)
        )

        self.url = reverse("payment-list-create")

    def test_access_denied_for_sales(self):
        self.client.force_authenticate(user=self.sales)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_access_allowed_for_manager_and_accountant(self):
        for user in [self.manager, self.accountant]:
            self.client.force_authenticate(user=user)
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_payment_updates_invoice_status(self):
        self.client.force_authenticate(user=self.accountant)
        data = {
            "invoice": self.invoice.id,
            "amount": 1000.00,
            "method": "cash", # lowercase لتطابق الـ choices
            "date": str(date.today()) # حقل date الإلزامي في موديل Payment
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.invoice.refresh_from_db()
        self.assertEqual(self.invoice.status, "paid")