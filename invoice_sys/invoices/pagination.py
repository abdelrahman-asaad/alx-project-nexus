# invoices/pagination.py
from rest_framework.pagination import PageNumberPagination

class InvoicePagination(PageNumberPagination):
    page_size = 10              # عدد العناصر في الصفحة
    page_size_query_param = 'page_size'
    max_page_size = 100
