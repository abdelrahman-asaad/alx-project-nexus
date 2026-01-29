import graphene
import products.schema # الملف اللي عملناه في الخطوة اللي فاتت

class Query(products.schema.Query, graphene.ObjectType):
    # هنا هتضيف الـ Queries من باقي التطبيقات زي (invoices.schema.Query) مستقبلاً
    pass

schema = graphene.Schema(query=Query)