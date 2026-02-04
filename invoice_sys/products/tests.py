from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Product, Category

User = get_user_model()

class ProductAPITestCase(APITestCase):
    def setUp(self):
        # 1. تحديث المستخدمين بالإيميل والأدوار الصغيرة (lowercase)
        self.owner = User.objects.create_user(email="owner@test.com", password="pass123", role="owner")
        self.manager = User.objects.create_user(email="manager@test.com", password="pass123", role="manager")
        self.user = User.objects.create_user(email="sales@test.com", password="pass123", role="sales")

        # إنشاء تصنيف للمنتجات
        self.category = Category.objects.create(name="Electronics")

        # إنشاء منتج
        self.product = Product.objects.create(
            name="Laptop",
            description="Gaming Laptop",
            price=1500,
            stock=10,
            category=self.category,
            status="available"
        )

        self.client = APIClient()

    def test_list_products_authenticated(self):
        # تسجيل الدخول بالإيميل
        self.client.login(email="sales@test.com", password="pass123")
        url = reverse("product-list-create")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Laptop", str(response.data))

    def test_create_product_permission(self):
        url = reverse("product-list-create")

        # محاولة إنشاء المنتج بمستخدم Sales (غالباً 403 حسب الـ logic)
        self.client.login(email="sales@test.com", password="pass123")
        response = self.client.post(url, {
            "name": "Phone",
            "description": "Smartphone",
            "price": 800,
            "stock": 20,
            "category": self.category.id,
            "status": "available"
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # إنشاء المنتج بواسطة Manager
        self.client.login(email="manager@test.com", password="pass123")
        response = self.client.post(url, {
            "name": "Phone",
            "description": "Smartphone",
            "price": 800,
            "stock": 20,
            "category": self.category.id,
            "status": "available"
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_product_permission(self):
        url = reverse("product-detail", args=[self.product.id])

        # تحديث بواسطة Sales (مرفوض)
        self.client.login(email="sales@test.com", password="pass123")
        response = self.client.put(url, {
            "name": "Laptop Updated",
            "price": 1600,
            "category": self.category.id
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # تحديث بواسطة Owner
        self.client.login(email="owner@test.com", password="pass123")
        response = self.client.put(url, {
            "name": "Laptop Updated",
            "description": "Updated Desc",
            "price": 1600,
            "stock": 8,
            "category": self.category.id,
            "status": "available"
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_product_permission(self):
        url = reverse("product-detail", args=[self.product.id])

        # حذف بواسطة Manager (مسموح)
        self.client.login(email="manager@test.com", password="pass123")
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_search_and_ordering(self):
        self.client.login(email="sales@test.com", password="pass123")
        url = reverse("product-list-create")
        
        # بحث باسم المنتج
        response = self.client.get(url + "?search=Laptop")
        # نتأكد من الـ pagination
        data = response.json()
        results = data.get('results', data)
        self.assertEqual(len(results), 1)