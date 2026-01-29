import graphene
from graphene_django import DjangoObjectType
from invoices.models import Invoice, InvoiceItem

# تحويل InvoiceItem لـ GraphQL Type
class InvoiceItemType(DjangoObjectType): #to convert InvoiceItem model to GraphQL type
    class Meta:
        model = InvoiceItem
        fields = ("id", "product", "quantity", "unit_price", "total_price") # fields to expose in GraphQL

# تحويل Invoice لـ GraphQL Type
class InvoiceType(DjangoObjectType):
    items = graphene.List(InvoiceItemType) # عشان نجيب الأصناف اللي جوه الفاتورة

    class Meta:
        model = Invoice
        # دي الحقول الحقيقية من الموديل بتاعك
        fields = ("id", "client", "user", "date", "due_date", "status", "total_amount", "items")

    def resolve_items(self, info):
        return self.items.all()

class Query(graphene.ObjectType):
    all_invoices = graphene.List(InvoiceType)
    invoice_by_id = graphene.Field(InvoiceType, id=graphene.Int()) #to get invoice by id and send it as argument

    def resolve_all_invoices(root, info):
        # select_related و prefetch_related عشان الأداء يكون طيارة
        return Invoice.objects.select_related('client', 'user').prefetch_related('items__product').all()

    def resolve_invoice_by_id(root, info, id):
        return Invoice.objects.get(pk=id)

schema = graphene.Schema(query=Query)

def resolve_invoice_by_id(root, info, id):
        try:
            return Invoice.objects.get(pk=id)
        except Invoice.DoesNotExist:
            return None # هيرجع null في الـ Playground بدل الـ Error
        
import graphene
from graphene_django import DjangoObjectType
from invoices.models import Invoice
from clients.models import Client # تأكد من استيراد موديل العميل

# 1. لازم نعرف الـ ClientType الأول عشان InvoiceType يشوفه
class ClientType(DjangoObjectType):
    class Meta:
        model = Client
        fields = ("id", "name") # أو الحقول اللي عندك في موديل العميل

class InvoiceType(DjangoObjectType):
    class Meta:
        model = Invoice
        fields = ("id", "status", "total_amount", "date", "client") # ضيف client هنا

class Query(graphene.ObjectType):
    all_invoices = graphene.List(InvoiceType)

    def resolve_all_invoices(root, info):
        # استخدام select_related بيخلي الكويري سريعة جداً
        return Invoice.objects.select_related('client').all()

schema = graphene.Schema(query=Query)


'''query {
  allInvoices {
    id
    status
    totalAmount
    client {
      name
    }
  }
}


query {
  invoiceById(id: 2) {
    id
    status
    totalAmount
  }
}
'''



class UpdateStatus(graphene.Mutation):
    # 1. إيه البيانات اللي المستلم هيبعتها؟
    class Arguments:
        invoice_id = graphene.Int(required=True)
        new_status = graphene.String(required=True)

    # 2. إيه البيانات اللي السيرفر هيرجعها بعد ما يخلص؟
    invoice = graphene.Field(InvoiceType)

    # 3. الأكشن اللي هيحصل فعلاً (القلب النابض)
    def mutate(self, info, invoice_id, new_status):
        invoice = Invoice.objects.get(pk=invoice_id)
        invoice.status = new_status
        invoice.save()
        return UpdateStatus(invoice=invoice)
    
# 1. عرف الـ Mutation Class (زي ما شرحناه في المرة اللي فاتت)
class Mutation(graphene.ObjectType):
    update_status = UpdateStatus.Field() # ده اسم العملية اللي هتناديها

# 2. اربط الـ Mutation بالـ Schema (ده الجزء اللي ناقص عندك غالباً)
schema = graphene.Schema(query=Query, mutation=Mutation)


'''mutation {
  updateStatus(invoiceId: 2, newStatus: "paid") {
    invoice {
      id
      status # هنا هيرجعلك PAID فوراً
    }
  }
}'''