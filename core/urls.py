from django.urls import path

from .views import DashboardView, health_check

app_name = "core"

urlpatterns = [
    path("panel/", DashboardView.as_view(), name="dashboard"),
    path("health/", health_check, name="health"),
]
