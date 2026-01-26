from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Product, Category

User = get_user_model()

class ProductAPITestCase(APITestCase):
    def setUp(self):
        # عمل مستخدمين بأدوار مختلفة
        self.owner = User.objects.create_user(username="owner", password="pass123", role="Owner")
        self.manager = User.objects.create_user(username="manager", password="pass123", role="Manager")
        self.user = User.objects.create_user(username="user", password="pass123", role="Sales")

        # انشاء تصنيف للمنتجات
        self.category = Category.objects.create(name="Electronics")

        # انشاء منتج
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
        self.client.login(username="user", password="pass123")
        url = reverse("product-list-create")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Laptop", str(response.data))

    def test_create_product_permission(self):
        url = reverse("product-list-create")

        # محاولة إنشاء المنتج بمستخدم عادي
        self.client.login(username="user", password="pass123")
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
        self.client.login(username="manager", password="pass123")
        response = self.client.post(url, {
            "name": "Phone",
            "description": "Smartphone",
            "price": 800,
            "stock": 20,
            "category": self.category.id,
            "status": "available"
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 2)

    def test_update_product_permission(self):
        url = reverse("product-detail", args=[self.product.id])

        # تحديث بواسطة مستخدم عادي
        self.client.login(username="user", password="pass123")
        response = self.client.put(url, {
            "name": "Laptop Updated",
            "description": "Updated Desc",
            "price": 1600,
            "stock": 8,
            "category": self.category.id,
            "status": "available"
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # تحديث بواسطة Owner
        self.client.login(username="owner", password="pass123")
        response = self.client.put(url, {
            "name": "Laptop Updated",
            "description": "Updated Desc",
            "price": 1600,
            "stock": 8,
            "category": self.category.id,
            "status": "available"
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, "Laptop Updated")

    def test_delete_product_permission(self):
        url = reverse("product-detail", args=[self.product.id])

        # حذف بواسطة مستخدم عادي
        self.client.login(username="user", password="pass123")
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # حذف بواسطة Manager
        self.client.login(username="manager", password="pass123")
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Product.objects.count(), 0)

    def test_search_and_ordering(self):
        self.client.login(username="user", password="pass123")
        url = reverse("product-list-create")
        
        # بحث باسم المنتج
        response = self.client.get(url + "?search=Laptop")
        self.assertEqual(len(response.data["results"]), 1)

        # ترتيب حسب السعر
        response = self.client.get(url + "?ordering=price")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
