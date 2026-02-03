import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.core.cache import cache

@pytest.fixture
def api_client():
    return APIClient()

@pytest.mark.django_db
class TestLoginThrottle:
    
    def setup_method(self):
        # تصفير الـ Redis قبل كل اختبار
        cache.clear()

    def test_activate_account_throttle(self, api_client):
        """
        اختبار الـ Throttle على كلاس ActivateAccountView 
        لأننا ضفنا فيه throttle_classes = [LoginThrottle]
        """
        # الاسم من ملف الـ urls بتاعك هو 'activate-account'
        url = reverse('activate-account')
        
        # إرسال 5 طلبات (الحد المسموح 5/min)
        # هنستخدم REMOTE_ADDR عشان AnonRateThrottle يشتغل صح
        for i in range(5):
            response = api_client.post(url, {'email': 'test@test.com', 'otp': '123456'}, REMOTE_ADDR='1.2.3.4')
            assert response.status_code != 429

        # الطلب السادس: لازم يترفض
        response = api_client.post(url, {'email': 'test@test.com', 'otp': '123456'}, REMOTE_ADDR='1.2.3.4')
        
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        print("\n✅ Success: Activate Account Throttled correctly!")

    def test_token_obtain_throttle(self, api_client):
        """
        اختبار الـ Throttle على رابط اللوجن (Token)
        """
        url = reverse('token_obtain_pair')
        
        # ملاحظة: TokenObtainPairView هيطبق الـ 'anon' throttle اللي في الـ settings (10/day)
        # أو لو عملت لها subclass وضفت لها الـ LoginThrottle
        for i in range(10): # جرب 10 مرات حسب الـ settings لـ 'anon'
            api_client.post(url, {'email': 'b@y.com', 'password': 'p'}, REMOTE_ADDR='9.9.9.9')
            
        response = api_client.post(url, {'email': 'b@y.com', 'password': 'p'}, REMOTE_ADDR='9.9.9.9')
        # ده هيعتمد على الـ 'anon' rate في الـ settings
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS