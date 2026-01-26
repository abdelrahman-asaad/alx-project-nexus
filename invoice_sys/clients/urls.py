from django.urls import path
from .views import ClientListView, ClientCreateView, ClientUpdateView, ClientDeleteView

urlpatterns = [
    # GET /api/Clients/ → List all
    path("", ClientListView.as_view(), name="client-list"),

    # POST /api/Clients/create/ → Create
    path("create/", ClientCreateView.as_view(), name="client-create"),

    # PUT /api/Clients/<id>/update/ → Update
    path("<int:pk>/update/", ClientUpdateView.as_view(), name="client-update"),

    # DELETE /api/Clients/<id>/delete/ → Delete
    path("<int:pk>/delete/", ClientDeleteView.as_view(), name="client-delete"),
]

