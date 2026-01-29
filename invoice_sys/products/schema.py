import graphene
from graphene_django import DjangoObjectType
from .models import Product, Category

# 1. تحويل الموديل لـ GraphQL Type
class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ("id", "name", "sale_price", "stock", "category")

class CategoryType(DjangoObjectType):
    class Meta:
        model = Category
        fields = ("id", "name")

# 2. إنشاء الـ Query (مكان الـ GET في REST)
class Query(graphene.ObjectType):
    all_products = graphene.List(ProductType)
    product_by_name = graphene.Field(ProductType, name=graphene.String())

    def resolve_all_products(root, info):
        # هنا بنستخدم الـ ORM العادي بتاعنا
        return Product.objects.select_related('category').all()

    def resolve_product_by_name(root, info, name):
        try:
            return Product.objects.get(name=name)
        except Product.DoesNotExist:
            return None