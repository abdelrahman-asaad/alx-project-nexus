# invoices/tests/test_views.py
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
        # Users
        self.owner = User.objects.create_user(username="owner", password="pass1234", role="Owner")
        self.manager = User.objects.create_user(username="manager", password="pass1234", role="Manager")
        self.sales = User.objects.create_user(username="sales", password="pass1234", role="Sales")

        # Client & Product
        self.client_obj = Client.objects.create(name="Client1", company_name="Company1")
        self.product = Product.objects.create(name="Prod1", cost_price=50, selling_price=100, stock=10)

        # Invoice
        self.invoice = Invoice.objects.create(client=self.client_obj, total_amount=0)
        self.invoice_item = InvoiceItem.objects.create(
            invoice=self.invoice,
            product=self.product,
            quantity=2,
            unit_price=self.product.selling_price,
            total_price=2*self.product.selling_price
        )
        self.invoice.total_amount = self.invoice_item.total_price
        self.invoice.save()

        # URLs
        self.list_create_url = reverse("invoice-list")  # اسم URL في urls.py
        self.detail_url = reverse("invoice-detail", kwargs={"pk": self.invoice.id})
        self.pdf_url = reverse("invoice-pdf", kwargs={"pk": self.invoice.id})

    def test_list_invoices_authenticated(self):
        self.client.force_authenticate(user=self.sales)
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)  # pagination موجودة

    def test_create_invoice_permission(self):
        self.client.force_authenticate(user=self.sales)
        data = {
            "client": self.client_obj.id,
            "items": [
                {"product": self.product.id, "quantity": 1, "unit_price": self.product.selling_price}
            ]
        }
        response = self.client.post(self.list_create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_invoice_permission(self):
        self.client.force_authenticate(user=self.manager)
        data = {"total_amount": 999}
        response = self.client.put(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.invoice.refresh_from_db()
        self.assertEqual(self.invoice.total_amount, 999)

    def test_delete_invoice_permission(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Invoice.objects.filter(id=self.invoice.id).exists())

    def test_pdf_export(self):
        self.client.force_authenticate(user=self.sales)
        response = self.client.get(self.pdf_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/pdf')
