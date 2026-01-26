from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Invoice
from .serializers import InvoiceSerializer
from .permissions import IsSalesOrManager, IsManager, IsOwner
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from .pagination import InvoicePagination

# ✅ List + Create (بيدعم Pagination + Filter + Search + Sorting)
class InvoiceListCreateView(generics.ListCreateAPIView):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    pagination_class = InvoicePagination
    # backends الخاصة بالبحث والترتيب والتصفية
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    # 🟢 التصفية بالحقول دي (client و status مثلاً)
    filterset_fields = ["client", "status"]

    # 🟢 البحث
    search_fields = ["id", "client__name"]

    # 🟢 الترتيب
    ordering_fields = ["date", "total_amount", "client__name"]

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsSalesOrManager()]  # إنشاء فاتورة -> Sales أو Manager
        return [IsAuthenticated()]       # عرض -> أي حد


# ✅ Retrieve + Update + Delete
class InvoiceRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    #to retrieve one invoice
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer

    def get_permissions(self):
        if self.request.method == "PUT":
            return [IsManager()]   # تعديل -> Manager فقط
        elif self.request.method == "DELETE":
            return [IsOwner()]     # حذف -> Owner فقط
        return [IsAuthenticated()] # عرض التفاصيل -> أي حد


# ✅ PDF Export
class InvoicePDFView(generics.RetrieveAPIView):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        invoice = self.get_object()
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="invoice_{invoice.id}.pdf"'

        p = canvas.Canvas(response)
        p.drawString(100, 800, f"Invoice #{invoice.id}")
        p.drawString(100, 780, f"Client: {invoice.client.name}")
        p.drawString(100, 760, f"Date: {invoice.date}")
        p.drawString(100, 740, f"Due Date: {invoice.due_date}")
        p.drawString(100, 720, f"Status: {invoice.status}")

        y = 700
        for item in invoice.items.all():
            p.drawString(120, y, f"{item.product.name} x {item.quantity} @ {item.unit_price} = {item.total_price}")
            y -= 20

        p.drawString(100, y-20, f"Total Amount: {invoice.total_amount}")
        p.showPage()
        p.save()
        return response

'''✅ كدا إيه اللي هيشتغل؟

/api/invoices/?client=1 ← فلترة بالعميل.

/api/invoices/?status=paid ← فلترة بالحالة.

/api/invoices/?search=Ahmed ← بحث باسم العميل أو رقم الفاتورة.

/api/invoices/?ordering=-date ← ترتيب تنازلي بالتاريخ.

/api/invoices/?ordering=total_amount ← ترتيب تصاعدي بقيمة الفاتورة.
'''