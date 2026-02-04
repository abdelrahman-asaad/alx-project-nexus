from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from .models import Client

User = get_user_model()

class ClientAPITests(APITestCase):

    def setUp(self):
        # تأكد إن الاسم هنا self.manager عشان التستات اللي تحت تشوفه
        self.manager = User.objects.create_user(
            email="manager@test.com", 
            password="password123", 
            role="manager", 
            is_staff=True
        )
        self.sales = User.objects.create_user(
            email="sales@test.com", 
            password="password123", 
            role="sales"
        )
        
        self.client_obj = Client.objects.create(
            name="Test Client",
            email="client@test.com",
            phone="123456789",
            company_name="Test Co",
            address="123 Street",
            created_by=self.manager
        )

        # الروابط بناءً على الـ urls.py بتاعك
        self.list_url = reverse("client-list")
        self.create_url = reverse("client-create")
        self.update_url = reverse("client-update", kwargs={"pk": self.client_obj.pk})
        self.delete_url = reverse("client-delete", kwargs={"pk": self.client_obj.pk})

    def test_list_clients_permissions(self):
        self.client.force_authenticate(user=self.manager)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_client_permissions(self):
        self.client.force_authenticate(user=self.sales)
        data = {
            "name": "New Client", "email": "n@c.com", 
            "phone": "123", "company_name": "C", "address": "A"
        }
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_client_permissions(self):
        self.client.force_authenticate(user=self.manager)
        response = self.client.patch(self.update_url, {"name": "Updated Name"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_client_permissions(self):
        self.client.force_authenticate(user=self.manager)
        response = self.client.delete(self.delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)