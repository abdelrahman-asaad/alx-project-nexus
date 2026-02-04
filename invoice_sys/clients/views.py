from rest_framework import generics, filters
from rest_framework.permissions import IsAuthenticated
from .models import Client
from .serializers import ClientSerializer
from .permissions import IsManager, IsSalesOrManager, IsOwnerOrManager
from django_filters.rest_framework import DjangoFilterBackend

# GET /api/clients/ – List all clients
class ClientListView(generics.ListAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    filterset_fields = ["company_name"]
    search_fields = ["name", "email", "company_name"]
    ordering_fields = ["name", "email", "company_name"]

    def get_queryset(self):
        # التعديل: استخدام الأدوار بصيغة lowercase لتطابق الموديل الجديد
        if self.request.user.role in ["manager", "sales", "owner"]:
            return Client.objects.all()
        return Client.objects.none()

# POST /api/clients/ – Create new client
class ClientCreateView(generics.CreateAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [IsSalesOrManager]
    
    def perform_create(self, serializer):
        # الربط مع المستخدم الحالي (الذي يستخدم الإيميل الآن)
        serializer.save(created_by=self.request.user)    

# PUT /api/clients/<int:pk>/ – Update client
class ClientUpdateView(generics.UpdateAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [IsManager]

# DELETE /api/clients/<int:pk>/ – Delete client
class ClientDeleteView(generics.DestroyAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [IsOwnerOrManager]