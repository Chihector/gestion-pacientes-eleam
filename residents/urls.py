from django.urls import path

from .views import (
    ContactCreateView,
    ContactDeleteView,
    ContactUpdateView,
    ResidentArchiveView,
    ResidentClinicalUpdateView,
    ResidentCreateView,
    ResidentDetailView,
    ResidentListView,
    ResidentUpdateView,
)

app_name = "residents"

urlpatterns = [
    path("", ResidentListView.as_view(), name="list"),
    path("nuevo/", ResidentCreateView.as_view(), name="create"),
    path("<int:pk>/", ResidentDetailView.as_view(), name="detail"),
    path("<int:pk>/editar/", ResidentUpdateView.as_view(), name="update"),
    path(
        "<int:pk>/clinico/",
        ResidentClinicalUpdateView.as_view(),
        name="clinical_update",
    ),
    path("<int:pk>/archivar/", ResidentArchiveView.as_view(), name="archive"),
    path(
        "<int:resident_pk>/contactos/nuevo/",
        ContactCreateView.as_view(),
        name="contact_create",
    ),
    path(
        "contactos/<int:pk>/editar/",
        ContactUpdateView.as_view(),
        name="contact_update",
    ),
    path(
        "contactos/<int:pk>/eliminar/",
        ContactDeleteView.as_view(),
        name="contact_delete",
    ),
]
