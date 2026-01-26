from rest_framework import generics, filters
from rest_framework.permissions import IsAuthenticated
from .models import Product
from .serializers import PublicProductSerializer, FullProductSerializer
from .permissions import IsManagerOrOwner
from django_filters.rest_framework import DjangoFilterBackend
#list and create
class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    # backends الخاصة بالبحث والترتيب والتصفية
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    #  التصفية بالحقول (زي التصنيف أو الحالة)
    filterset_fields = ["category", "stock"]

    #  البحث (بالاسم أو الوصف مثلاً)
    search_fields = ["id", "name", "description"]

    #  الترتيب
    ordering_fields = ["sale_price", "stock", "name"]

    def get_serializer_class(self):
        user = self.request.user
        if user.is_authenticated and user.role.lower() in ["manager", "owner"]:

            return FullProductSerializer
        return PublicProductSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsManagerOrOwner()]  # Create -> Manager/Owner
        return [IsAuthenticated()]      # GET -> أي حد عامل Login

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
