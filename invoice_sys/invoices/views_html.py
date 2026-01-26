from django.shortcuts import render
from django.views.decorators.cache import never_cache


@never_cache
def invoice_list_page(request):
    """ صفحة عرض آخر الفواتير + زر إنشاء جديد """
    return render(request, "invoices/invoice_list.html")


def invoice_create_page(request):
    """ صفحة إنشاء فاتورة جديدة + إضافة عناصرها """
    return render(request, "invoices/invoice_create.html")
