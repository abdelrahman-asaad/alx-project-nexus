import graphene
from graphene_django import DjangoObjectType
from .models import Client

# 1. تعريف الـ Type الخاص بالعميل
class ClientType(DjangoObjectType):
    class Meta:
        model = Client
        # تأكد من إضافة كل الحقول التي ستحتاجها في الداشبورد
        fields = ("id", "name", "email", "invoices") 

# 2. تعريف الـ Queries الخاصة بالعملاء
class Query(graphene.ObjectType):
    all_clients = graphene.List(ClientType)
    client_by_id = graphene.Field(ClientType, id=graphene.ID(required=True))

    def resolve_all_clients(root, info):
    # استخدام prefetch_related بيجيب كل الفواتير في خبطة واحدة (2 Queries بس بدل 11)
     return Client.objects.prefetch_related('invoices').all()
    def resolve_client_by_id(root, info, id):
        try:
            return Client.objects.get(pk=id)
        except Client.DoesNotExist:
            return None