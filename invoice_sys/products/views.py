from rest_framework import generics, filters
from rest_framework.permissions import IsAuthenticated
from .models import Product
from .serializers import PublicProductSerializer, FullProductSerializer
from .permissions import IsManagerOrOwner
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers # مهم جداً للأمان

class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    
    # 1. بنكّيش لمدة ساعتين
    # 2. بنستخدم vary_on_headers عشان الكاش يفصل نسخة لكل "توكين" 
    # كدة الـ Manager هياخد نسخة والـ Sales هياخد نسخة تانية خالص
    @method_decorator(cache_page(60 * 60 * 2))
    @method_decorator(vary_on_headers("Authorization")) 
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["category", "stock"]
    search_fields = ["id", "name", "description"]
    ordering_fields = ["sale_price", "stock", "name"]
    
    def get_serializer_class(self):
        user = self.request.user
        if user.is_authenticated and user.role.lower() in ["manager", "owner"]:
            return FullProductSerializer
        return PublicProductSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsManagerOrOwner()]
        return [IsAuthenticated()]
#retrive , update and delete
class ProductRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()

    def get_serializer_class(self):
        user = self.request.user
        if user.is_authenticated and user.role.lower() in ["manager", "owner"]:
            return FullProductSerializer
        return PublicProductSerializer

    def get_permissions(self):
        if self.request.method in ["PUT", "DELETE"]:
            return [IsManagerOrOwner()]  # Update/Delete -> Manager/Owner
        return [IsAuthenticated()]      # GET -> أي حد عامل Login
