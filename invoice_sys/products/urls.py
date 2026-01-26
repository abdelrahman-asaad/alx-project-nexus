from django.urls import path
from .views import (
   ProductListCreateView,
   ProductRetrieveUpdateDeleteView
)

from django.urls import path
from .views import ProductListCreateView, ProductRetrieveUpdateDeleteView

urlpatterns = [
    # /api/products/ → List + Create
    path("", ProductListCreateView.as_view(), name="product-list-create"),

    # /api/products/<id>/ → Retrieve + Update + Delete
    path("<int:pk>/", ProductRetrieveUpdateDeleteView.as_view(), name="product-detail"),
]
