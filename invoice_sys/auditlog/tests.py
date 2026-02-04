from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import AuditLog

User = get_user_model()

class AuditLogTests(APITestCase):

    def setUp(self):
        # 1. إنشاء المستخدمين (تأكد من أن الـ Role lowercase)
        self.admin_user = User.objects.create_user(
            email="admin@test.com", 
            password="password123", 
            role="manager", 
            is_staff=True
        )
        self.regular_user = User.objects.create_user(
            email="user@test.com", 
            password="password123", 
            role="sales"
        )

        # 2. إنشاء سجلات
        self.log1 = AuditLog.objects.create(
            user=self.admin_user,
            action="create",
            model_name="Invoice",
            object_id=1,
            changes_summary="Created a new invoice"
        )

        self.url = reverse("auditlog-list")

    def test_list_audit_logs_as_admin(self):
        # الحل: استخدام force_authenticate بدلاً من login
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_audit_logs_forbidden_for_regular_user(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(self.url)
        # لو الـ View متبرمجة صح، هترجع 403 للموظف العادي
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_filter_by_action(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.url, {"action": "create"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        results = data.get('results', data)
        self.assertEqual(results[0]["action"], "create")

    def test_search_by_model_name(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.url, {"search": "Invoice"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)