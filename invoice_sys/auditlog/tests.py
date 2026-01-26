from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import AuditLog
from datetime import datetime, timedelta

User = get_user_model()

class AuditLogTests(APITestCase):
    def setUp(self):
        # إنشاء مستخدمين
        self.admin = User.objects.create_user(username="admin", password="admin123", is_staff=True)
        self.superuser = User.objects.create_superuser(username="superuser", password="super123")
        self.regular_user = User.objects.create_user(username="user", password="user123")

        # إنشاء AuditLog records
        self.log1 = AuditLog.objects.create(
            user=self.admin, action="create", description="Admin created something", timestamp=datetime.now()
        )
        self.log2 = AuditLog.objects.create(
            user=self.superuser, action="delete", description="Superuser deleted something", timestamp=datetime.now() - timedelta(days=1)
        )
        self.log3 = AuditLog.objects.create(
            user=self.admin, action="update", description="Admin updated something", timestamp=datetime.now() - timedelta(days=2)
        )

        self.url = reverse("auditlog-list")

    # اختبار صلاحيات الوصول
    def test_permission_for_admin_and_superuser(self):
        # Admin
        self.client.login(username="admin", password="admin123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.logout()

        # Superuser
        self.client.login(username="superuser", password="super123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.logout()

    def test_permission_for_regular_user(self):
        self.client.login(username="user", password="user123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.client.logout()

    # اختبار ترتيب السجلات افتراضياً
    def test_default_ordering(self):
        self.client.login(username="admin", password="admin123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        timestamps = [entry["timestamp"] for entry in response.json()]
        self.assertTrue(timestamps[0] >= timestamps[1] >= timestamps[2])
        self.client.logout()

    # اختبار الفلاتر
    def test_filter_by_user(self):
        self.client.login(username="admin", password="admin123")
        response = self.client.get(self.url, {"user": self.admin.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for entry in response.json():
            self.assertEqual(entry["user"], self.admin.id)
        self.client.logout()

    def test_filter_by_action(self):
        self.client.login(username="admin", password="admin123")
        response = self.client.get(self.url, {"action": "delete"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for entry in response.json():
            self.assertEqual(entry["action"], "delete")
        self.client.logout()

    # اختبار البحث
    def test_search_by_description(self):
        self.client.login(username="admin", password="admin123")
        response = self.client.get(self.url, {"search": "updated"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(any("updated" in entry["description"] for entry in response.json()))
        self.client.logout()

    # اختبار ترتيب حسب user__username
    def test_ordering_by_user(self):
        self.client.login(username="admin", password="admin123")
        response = self.client.get(self.url, {"ordering": "user__username"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        usernames = [entry["user"] for entry in response.json()]
        self.assertEqual(usernames, sorted(usernames))
        self.client.logout()
