from django.urls import path
from .views import SalesSummaryView, ProfitTrackerView, dashboard_page

urlpatterns = [
    path('sales-summary/', SalesSummaryView.as_view(), name='sales-summary'),
    path('profit-tracker/', ProfitTrackerView.as_view(), name='profit-tracker'),
    path('', dashboard_page, name='dashboard'),
]
