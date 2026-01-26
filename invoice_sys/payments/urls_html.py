from django.urls import path
from django.http import HttpResponse

def payments_page(request):
    return HttpResponse("Payments HTML page coming soon!")

urlpatterns = [
    path('', payments_page, name='payments_page'),
]
