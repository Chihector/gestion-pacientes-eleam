from django.urls import path

from .views import (
    IncidentCloseView,
    IncidentCreateView,
    IncidentDetailView,
    IncidentExportView,
    IncidentListView,
    IncidentReportView,
)

app_name = "incidents"

urlpatterns = [
    path("", IncidentListView.as_view(), name="list"),
    path("nuevo/", IncidentCreateView.as_view(), name="create"),
    path("informes/", IncidentReportView.as_view(), name="reports"),
    path("exportar/", IncidentExportView.as_view(), name="export"),
    path("<int:pk>/", IncidentDetailView.as_view(), name="detail"),
    path("<int:pk>/cerrar/", IncidentCloseView.as_view(), name="close"),
]
