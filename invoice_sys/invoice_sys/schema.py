import graphene
import graphql_jwt
import products.schema
import invoices.schema
import clients.schema
import dashboard.schema

# 1. تجميع كل الـ Queries
class Query(
    products.schema.Query,
    clients.schema.Query,
    dashboard.schema.DashboardQuery,
    graphene.ObjectType
):
    pass

# 2. تجميع كل الـ Mutations (عشان الـ Token يشتغل)
class Mutation(graphene.ObjectType):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()

# 3. تعريف الـ Schema مرة واحدة فقط بتجمع الاتنين
schema = graphene.Schema(query=Query, mutation=Mutation)