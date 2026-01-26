from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Client

User = get_user_model()

class ClientAPITests(APITestCase):
    def setUp(self):
        # إنشاء مستخدمين بأدوار مختلفة
        self.owner = User.objects.create_user(username="owner", password="owner123", role="Owner")
        self.manager = User.objects.create_user(username="manager", password="manager123", role="Manager")
        self.sales = User.objects.create_user(username="sales", password="sales123", role="Sales")
        self.regular = User.objects.create_user(username="user", password="user123", role="User")

        # إنشاء بعض الـ clients
        self.client1 = Client.objects.create(name="Client1", email="c1@test.com", company_name="CompanyA")
        self.client2 = Client.objects.create(name="Client2", email="c2@test.com", company_name="CompanyB")

    # اختبار صلاحيات الوصول لقائمة العملاء
    def test_list_clients_permissions(self):
        # Owner
        self.client.login(username="owner", password="owner123")
        response = self.client.get(reverse("client-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.logout()

        # Manager
        self.client.login(username="manager", password="manager123")
        response = self.client.get(reverse("client-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.logout()

        # Sales
        self.client.login(username="sales", password="sales123")
        response = self.client.get(reverse("client-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.logout()

        # Regular user
        self.client.login(username="user", password="user123")
        response = self.client.get(reverse("client-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)  # ممكن يرجع none بس 200
        self.client.logout()

    # اختبار إنشاء العميل
    def test_create_client_permissions(self):
        data = {"name": "Client3", "email": "c3@test.com", "company_name": "CompanyC"}

        # Sales يقدر يعمل POST
        self.client.login(username="sales", password="sales123")
        response = self.client.post(reverse("client-create"), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.client.logout()

        # Regular user مش هينجح
        self.client.login(username="user", password="user123")
        response = self.client.post(reverse("client-create"), data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.client.logout()

    # اختبار تحديث العميل
    def test_update_client_permissions(self):
        data = {"name": "UpdatedClient"}
        url = reverse("client-update", kwargs={"pk": self.client1.id})

        # Manager يقدر يعمل PUT
        self.client.login(username="manager", password="manager123")
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.logout()

        # Sales مش هيقدر
        self.client.login(username="sales", password="sales123")
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.client.logout()

    # اختبار حذف العميل
    def test_delete_client_permissions(self):
        url = reverse("client-delete", kwargs={"pk": self.client2.id})

        # Owner يقدر DELETE
        self.client.login(username="owner", password="owner123")
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.client.logout()

        # Manager يقدر DELETE
        self.client.login(username="manager", password="manager123")
        response = self.client.delete(url)
        self.assertIn(response.status_code, [status.HTTP_204_NO_CONTENT, status.HTTP_404_NOT_FOUND])
        self.client.logout()

        # Sales مش هيقدر
        self.client.login(username="sales", password="sales123")
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.client.logout()
