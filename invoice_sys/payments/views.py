from rest_framework import generics, filters
from .models import Payment
from .serializers import PaymentSerializer
from .permissions import IsAccountantOrManager
from django_filters.rest_framework import DjangoFilterBackend

class PaymentListCreateView(generics.ListCreateAPIView): #create and list views
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    filterset_fields = ["invoice", "user", "method"]
    search_fields = ["user__username", "invoice__id", "method"]
    ordering_fields = ["date", "amount", "user__username"]

    def get_permissions(self): #override this built-in method to declare which permissions are used
        return [IsAccountantOrManager()]

    def perform_create(self, serializer): #override this built-in method to save user when POST new payment
        payment = serializer.save(user=self.request.user) #creating payment object from Payment class 
  # حساب إجمالي المدفوعات
        invoice = payment.invoice #invoice field which is foreignkey to Invoice model , to bring
        
        #invoice of payment as an object of Inovice class
        
        total_paid = sum(p.amount for p in invoice.payments.all()) #payments is the related_name in
        
        #invoice field
#to bring all payments in invoice
        
        # تحديث حالة الفاتورة بناءً على المبلغ
        if total_paid >= invoice.total_amount:
            invoice.status = "paid"
        elif total_paid > 0:
            invoice.status = "unpaid"  # لسه متسددش بالكامل
        else:
            invoice.status = "overdue"

        invoice.save()