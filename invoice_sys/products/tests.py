from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from products.models import Product
from django.core.cache import cache

User = get_user_model()

class ProductAPITestCase(APITestCase):

    def setUp(self):
        # تنظيف الكاش لضمان دقة الاختبارات
        cache.clear()

        # 1. إنشاء المستخدمين بأدوار lowercase
        self.owner = User.objects.create_user(email="owner@test.com", password="pass1234", role="owner")
        self.manager = User.objects.create_user(email="manager@test.com", password="pass1234", role="manager")
        self.sales = User.objects.create_user(email="sales@test.com", password="pass1234", role="sales")

        # 2. إنشاء منتج تجريبي (باستخدام sale_price وبدون status)
        self.product = Product.objects.create(
            name="Test Product",
            description="Sample description",
            sale_price=100.00,
            cost_price=70.00,
            stock=10,
            currency="USD"
        )

        # الروابط (تأكد من مطابقتها لملف urls.py عندك)
        self.list_create_url = reverse("product-list-create")
        self.detail_url = reverse("product-detail", kwargs={"pk": self.product.id})

    def test_list_products_authenticated(self):
        self.client.force_authenticate(user=self.sales)
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_product_permission(self):
        self.client.force_authenticate(user=self.owner)
        data = {
            "name": "New Product",
            "sale_price": 150.00,
            "cost_price": 100.00,
            "stock": 5
        }
        response = self.client.post(self.list_create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_product_permission(self):
        self.client.force_authenticate(user=self.manager)
        data = {"sale_price": 120.00}
        response = self.client.patch(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertEqual(float(self.product.sale_price), 120.00)

    def test_delete_product_permission(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_search_and_ordering(self):
        self.client.force_authenticate(user=self.sales)
        # تجربة البحث بالاسم
        response = self.client.get(f"{self.list_create_url}?search=Test")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # تجربة الترتيب بالسعر
        response = self.client.get(f"{self.list_create_url}?ordering=-sale_price")
        self.assertEqual(response.status_code, status.HTTP_200_OK)