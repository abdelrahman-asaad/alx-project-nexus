from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import AuditLog
from datetime import datetime, timedelta

User = get_user_model()

class AuditLogTests(APITestCase):
    def setUp(self):
        # 1. تعديل إنشاء المستخدمين (استبدال username بـ email)
        self.admin = User.objects.create_user(email="admin@test.com", password="admin123", is_staff=True)
        self.superuser = User.objects.create_superuser(email="superuser@test.com", password="super123")
        self.regular_user = User.objects.create_user(email="user@test.com", password="user123")

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
        # Admin - التعديل لاستخدام email في الـ login
        self.client.login(email="admin@test.com", password="admin123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.logout()

        # Superuser
        self.client.login(email="superuser@test.com", password="super123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.logout()

    def test_permission_for_regular_user(self):
        self.client.login(email="user@test.com", password="user123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.client.logout()

    # اختبار ترتيب السجلات افتراضياً
    def test_default_ordering(self):
        self.client.login(email="admin@test.com", password="admin123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # ملاحظة: لو كنت مفعل Pagination، الداتا هتكون جوه مفتاح اسمه "results"
        data = response.json()
        results = data.get('results', data) # يتكيف مع وجود باجينيشن أو عدمه
        
        timestamps = [entry["timestamp"] for entry in results]
        # التأكد من الترتيب التنازلي (الأحدث أولاً)
        self.assertTrue(all(timestamps[i] >= timestamps[i+1] for i in range(len(timestamps)-1)))
        self.client.logout()

    # اختبار الفلاتر
    def test_filter_by_user(self):
        self.client.login(email="admin@test.com", password="admin123")
        response = self.client.get(self.url, {"user": self.admin.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        results = data.get('results', data)
        for entry in results:
            self.assertEqual(entry["user"], self.admin.id)
        self.client.logout()

    def test_filter_by_action(self):
        self.client.login(email="admin@test.com", password="admin123")
        response = self.client.get(self.url, {"action": "delete"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        results = data.get('results', data)
        for entry in results:
            self.assertEqual(entry["action"], "delete")
        self.client.logout()

    # اختبار البحث
    def test_search_by_description(self):
        self.client.login(email="admin@test.com", password="admin123")
        response = self.client.get(self.url, {"search": "updated"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        results = data.get('results', data)
        self.assertTrue(any("updated" in entry["description"] for entry in results))
        self.client.logout()

    # اختبار الترتيب حسب الإيميل (بدل اليوزرنيم)
    def test_ordering_by_user_email(self):
        self.client.login(email="admin@test.com", password="admin123")
        # التعديل هنا ليكون user__email لأن مفيش username
        response = self.client.get(self.url, {"ordering": "user__email"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        results = data.get('results', data)
        emails = [entry["user"] for entry in results] # افترضنا أن الـ serializer يرجع الـ ID أو الإ