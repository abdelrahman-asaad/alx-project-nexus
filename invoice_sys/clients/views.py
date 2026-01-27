from rest_framework import generics, filters
from rest_framework.permissions import IsAuthenticated
from .models import Client
from .serializers import ClientSerializer
from .permissions import IsManager, IsSalesOrManager, IsOwnerOrManager
from django_filters.rest_framework import DjangoFilterBackend

# GET /api/clients/ – List all clients (Manager, Sales, Owner)
class ClientListView(generics.ListAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated]  # check role in logic
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    filterset_fields = ["company_name"]
    search_fields = ["name", "email", "company_name"]
    ordering_fields = ["name", "email", "company_name"]

    def get_queryset(self):
        # Managers, Sales, Owner can see
        if self.request.user.role in ["Manager", "Sales", "Owner"]:
            return Client.objects.all()
        return Client.objects.none()

# POST /api/clients/ – Create new client (Sales, Manager)
class ClientCreateView(generics.CreateAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [IsSalesOrManager]
    def perform_create(self, serializer):
        # self.request.user هو المستخدم صاحب الـ Token الحالي
        serializer.save(created_by=self.request.user)    

# PUT /api/clients/<int:pk>/ – Update client (Manager only)
class ClientUpdateView(generics.UpdateAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [IsManager]

# DELETE /api/clients/<int:pk>/ – Delete client (Owner or Manager)
class ClientDeleteView(generics.DestroyAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [IsOwnerOrManager]
