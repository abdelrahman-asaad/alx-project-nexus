from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class AccountsAPITest(APITestCase):

    def setUp(self):
        # إنشاء مستخدم Owner
        self.owner = User.objects.create_user(
            username="owner", email="owner@test.com", password="ownerpass", role="Owner"
        )
        # إنشاء مستخدم Manager
        self.manager = User.objects.create_user(
            username="manager", email="manager@test.com", password="managerpass", role="Manager"
        )
        # إنشاء مستخدم عادي
        self.sales = User.objects.create_user(
            username="sales", email="sales@test.com", password="salespass", role="Sales"
        )

    def test_register_view(self):
        """ أي شخص يقدر يعمل تسجيل مستخدم جديد """
        url = reverse('register')  
        data = {
            "username": "newuser",
            "email": "newuser@test.com",
            "password": "newpass123"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_user_list_owner_access(self):
        """ Owner يقدر يشوف قائمة المستخدمين """
        self.client.force_authenticate(user=self.owner)
        url = reverse('user-list')  
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 3)

    def test_user_list_manager_access(self):
        """ Manager يقدر يشوف قائمة المستخدمين """
        self.client.force_authenticate(user=self.manager)
        url = reverse('user-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_list_sales_access_denied(self):
        """ Sales لا يقدر يشوف المستخدمين """
        self.client.force_authenticate(user=self.sales)
        url = reverse('user-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_user_role_owner(self):
        """ Owner يقدر يغير دور مستخدم """
        self.client.force_authenticate(user=self.owner)
        url = reverse('update-user-role', kwargs={"pk": self.sales.pk})
        data = {"role": "Manager"}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.sales.refresh_from_db()
        self.assertEqual(self.sales.role, "Manager")

    def test_update_user_role_non_owner(self):
        """ أي شخص غير Owner لا يقدر يغير دور مستخدم """
        self.client.force_authenticate(user=self.manager)
        url = reverse('update-user-role', kwargs={"pk": self.sales.pk})
        data = {"role": "Manager"}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
