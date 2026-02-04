from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class AccountsAPITest(APITestCase):

    def setUp(self):
        # إنشاء مستخدمين بالأدوار الصحيحة (Lowercase كما في الموديل)
        self.owner = User.objects.create_user(
            email="owner@test.com", password="ownerpass", role="owner"
        )
        self.manager = User.objects.create_user(
            email="manager@test.com", password="managerpass", role="manager"
        )
        self.sales = User.objects.create_user(
            email="sales@test.com", password="salespass", role="sales"
        )

    def test_activate_view_exists(self):
        """ التأكد من أن رابط التفعيل (activate) يعمل ويستقبل البيانات """
        url = reverse('activate-account')  
        data = {
            "email": "newuser@test.com",
            "otp": "123456"
        }
        response = self.client.post(url, data, format='json')
        # حتى لو الـ OTP غلط، المهم إن الرابط موجود (NoReverseMatch مش هتحصل)
        # والرد غالباً هيكون 400 أو 404 حسب الـ Logic عندك، وده معناه إن الرابط شغال
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND, status.HTTP_200_OK])

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
        data = {"role": "manager"}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.sales.refresh_from_db()
        self.assertEqual(self.sales.role, "manager")

    def test_update_user_role_non_owner(self):
        """ أي شخص غير Owner لا يقدر يغير دور مستخدم """
        self.client.force_authenticate(user=self.manager)
        url = reverse('update-user-role', kwargs={"pk": self.sales.pk})
        data = {"role": "manager"}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)