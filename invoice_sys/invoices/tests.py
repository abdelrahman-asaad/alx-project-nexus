from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from invoices.models import Invoice, InvoiceItem
from clients.models import Client
from products.models import Product

User = get_user_model()

class InvoiceViewTests(APITestCase):

    def setUp(self):
        # 1. تحديث إنشاء المستخدمين بالإيميل والأدوار الصغيرة (lowercase)
        self.owner = User.objects.create_user(email="owner@test.com", password="pass1234", role="owner")
        self.manager = User.objects.create_user(email="manager@test.com", password="pass1234", role="manager")
        self.sales = User.objects.create_user(email="sales@test.com", password="pass1234", role="sales")

        # Client & Product
        self.client_obj = Client.objects.create(name="Client1", company_name="Company1")
        # تأكد من مسمى الحقل selling_price أو price حسب الموديل عندك
        self.product = Product.objects.create(name="Prod1", cost_price=50, price=100, stock=10)

        # Invoice
        self.invoice = Invoice.objects.create(client=self.client_obj, total_amount=0)
        self.invoice_item = InvoiceItem.objects.create(
            invoice=self.invoice,
            product=self.product,
            quantity=2,
            unit_price=100, # استبدلتها بـ 100 مباشرة للتأكد
            total_price=200
        )
        self.invoice.total_amount = 200
        self.invoice.save()

        # URLs
        self.list_create_url = reverse("invoice-list")
        self.detail_url = reverse("invoice-detail", kwargs={"pk": self.invoice.id})
        self.pdf_url = reverse("invoice-pdf", kwargs={"pk": self.invoice.id})

    def test_list_invoices_authenticated(self):
        # استخدام force_authenticate سليم لأنه يمرر الكائن مباشرة
        self.client.force_authenticate(user=self.sales)
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # إذا كان الرد قائمة مباشرة أو Pagination
        data = response.json()
        if isinstance(data, dict) and "results" in data:
            self.assertIn("results", data)
        else:
            self.assertIsInstance(data, list)

    def test_create_invoice_permission(self):
        self.client.force_authenticate(user=self.sales)
        data = {
            "client": self.client_obj.id,
            "items": [
                {"product": self.product.id, "quantity": 1, "unit_price": 100}
            ]
        }
        response = self.client.post(self.list_create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_invoice_permission(self):
        # الـ Manager غالباً له صلاحية التعديل
        self.client.force_authenticate(user=self.manager)
        data = {"total_amount": 999}
        response = self.client.put(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.invoice.refresh_from_db()
        self.assertEqual(float(self.invoice.total_amount), 999.0)

    def test_delete_invoice_permission(self):
        # الـ Owner فقط هو من يحذف عادة
        self.client.force_authenticate(user=self.owner)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Invoice.objects.filter(id=self.invoice.id).exists())

    def test_pdf_export(self):
        self.client.force_authenticate(user=self.sales)
        response = self.client.get(self.pdf_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/pdf')