from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from invoices.models import Invoice, InvoiceItem
from clients.models import Client
from products.models import Product
from datetime import date, timedelta

User = get_user_model()

class InvoiceViewTests(APITestCase):

    def setUp(self):
        # 1. إنشاء المستخدمين (الأدوار lowercase)
        self.owner = User.objects.create_user(email="owner@test.com", password="pass1234", role="owner")
        self.manager = User.objects.create_user(email="manager@test.com", password="pass1234", role="manager")
        self.sales = User.objects.create_user(email="sales@test.com", password="pass1234", role="sales")

        # 2. إنشاء العميل (مع إضافة created_by لأنه BaseModel)
        self.client_obj = Client.objects.create(
            name="Client1", 
            company_name="Company1", 
            created_by=self.owner
        )

        # 3. إنشاء المنتج (الحقل الصحيح هو sale_price بناءً على كودك السابق)
        self.product = Product.objects.create(
            name="Prod1", 
            cost_price=50.00, 
            sale_price=100.00, 
            stock=10
        )

        # 4. إنشاء الفاتورة (بكل الحقول الإلزامية اللي شفناها في الموديل)
        today = date.today()
        self.invoice = Invoice.objects.create(
            client=self.client_obj, 
            user=self.owner,      # حقل user الإلزامي
            date=today,           # حقل date الإلزامي
            due_date=today + timedelta(days=7), # حقل due_date الإلزامي
            total_amount=200.00
        )
        
        # 5. إنشاء بند الفاتورة (بدون total_price لأنه @property)
        self.invoice_item = InvoiceItem.objects.create(
            invoice=self.invoice,
            product=self.product,
            quantity=2,
            unit_price=100.00
        )

        # 🔗 تحديث الروابط بناءً على urls.py الفعلي
        self.list_create_url = reverse("invoice-list-create") # التعديل هنا
        self.detail_url = reverse("invoice-detail", kwargs={"pk": self.invoice.id})
        self.pdf_url = reverse("invoice-pdf", kwargs={"pk": self.invoice.id})

    def test_list_invoices_authenticated(self):
        self.client.force_authenticate(user=self.sales)
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_invoice_permission(self):
        self.client.force_authenticate(user=self.sales)
        today = date.today()
        data = {
            "client": self.client_obj.id,
            "user": self.sales.id,
            "date": str(today),
            "due_date": str(today + timedelta(days=14)),
            "items": [
                {"product": self.product.id, "quantity": 1, "unit_price": 100}
            ]
        }
        response = self.client.post(self.list_create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_invoice_permission(self):
        self.client.force_authenticate(user=self.manager)
        data = {"total_amount": 999.00}
        # استخدم patch للتعديل الجزئي
        response = self.client.patch(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_invoice_permission(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_pdf_export(self):
        self.client.force_authenticate(user=self.sales)
        response = self.client.get(self.pdf_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/pdf')