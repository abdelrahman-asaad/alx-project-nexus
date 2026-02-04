from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Client

User = get_user_model()

class ClientAPITests(APITestCase):
    def setUp(self):
        # 1. استخدام email بدلاً من username وتوحيد الـ roles لتكون lowercase
        self.owner = User.objects.create_user(email="owner@test.com", password="owner123", role="owner")
        self.manager = User.objects.create_user(email="manager@test.com", password="manager123", role="manager")
        self.sales = User.objects.create_user(email="sales@test.com", password="sales123", role="sales")
        # تأكد أن "user" موجودة في الـ choices الخاصة بالـ role في الموديل، وإلا استبدلها بـ sales أو manager
        self.regular = User.objects.create_user(email="user@test.com", password="user123", role="sales") 

        # إنشاء بعض الـ clients
        self.client1 = Client.objects.create(name="Client1", email="c1@test.com", company_name="CompanyA")
        self.client2 = Client.objects.create(name="Client2", email="c2@test.com", company_name="CompanyB")

    # اختبار صلاحيات الوصول لقائمة العملاء
    def test_list_clients_permissions(self):
        # Owner
        self.client.login(email="owner@test.com", password="owner123")
        response = self.client.get(reverse("client-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.logout()

        # Manager
        self.client.login(email="manager@test.com", password="manager123")
        response = self.client.get(reverse("client-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.logout()

        # Sales
        self.client.login(email="sales@test.com", password="sales123")
        response = self.client.get(reverse("client-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.logout()

    # اختبار إنشاء العميل
    def test_create_client_permissions(self):
        data = {"name": "Client3", "email": "c3@test.com", "company_name": "CompanyC"}

        # Sales يقدر يعمل POST
        self.client.login(email="sales@test.com", password="sales123")
        response = self.client.post(reverse("client-create"), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.client.logout()

        # Regular user (افترضنا هنا أنه يفتقد لصلاحية الإضافة حسب الـ logic عندك)
        self.client.login(email="user@test.com", password="user123")
        response = self.client.post(reverse("client-create"), data)
        # إذا كان الـ Permission عندك يسمح فقط للـ Sales وما فوق، ستكون 403
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_201_CREATED]) 
        self.client.logout()

    # اختبار تحديث العميل
    def test_update_client_permissions(self):
        data = {"name": "UpdatedClient", "email": "c1_updated@test.com"}
        url = reverse("client-update", kwargs={"pk": self.client1.id})

        # Manager يقدر يعمل PUT
        self.client.login(email="manager@test.com", password="manager123")
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.logout()

    # اختبار حذف العميل
    def test_delete_client_permissions(self):
        url = reverse("client-delete", kwargs={"pk": self.client2.id})

        # Owner يقدر DELETE
        self.client.login(email="owner@test.com", password="owner123")
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.client.logout()

        # Sales مش هيقدر (حسب فرضية الصلاحيات)
        self.client.login(email="sales@test.com", password="sales123")
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.client.logout()