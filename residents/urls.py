from django.urls import path

from .views import (
    ContactCreateView,
    ContactDeleteView,
    ContactUpdateView,
    DiseaseCreateView,
    DiseaseDeleteView,
    DiseaseUpdateView,
    MedicationCreateView,
    MedicationDeleteView,
    MedicationUpdateView,
    ResidentArchiveView,
    ResidentClinicalUpdateView,
    ResidentCreateView,
    ResidentDetailView,
    ResidentExportView,
    ResidentListView,
    ResidentUpdateView,
)

app_name = "residents"

urlpatterns = [
    path("", ResidentListView.as_view(), name="list"),
    path("nuevo/", ResidentCreateView.as_view(), name="create"),
    path("exportar/", ResidentExportView.as_view(), name="export"),
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
    path(
        "<int:resident_pk>/enfermedades/nueva/",
        DiseaseCreateView.as_view(),
        name="disease_create",
    ),
    path(
        "enfermedades/<int:pk>/editar/",
        DiseaseUpdateView.as_view(),
        name="disease_update",
    ),
    path(
        "enfermedades/<int:pk>/eliminar/",
        DiseaseDeleteView.as_view(),
        name="disease_delete",
    ),
    path(
        "<int:resident_pk>/medicamentos/nuevo/",
        MedicationCreateView.as_view(),
        name="medication_create",
    ),
    path(
        "medicamentos/<int:pk>/editar/",
        MedicationUpdateView.as_view(),
        name="medication_update",
    ),
    path(
        "medicamentos/<int:pk>/eliminar/",
        MedicationDeleteView.as_view(),
        name="medication_delete",
    ),
]
