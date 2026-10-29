from django.urls import path

from .views import (
    CarePlanCloseView,
    CarePlanCreateView,
    CarePlanReopenView,
    CarePlanUpdateView,
    DailyCareRecordCorrectView,
    DailyCareRecordCreateView,
    DailyCareRecordDetailView,
    DailyCareRecordListView,
    DailyCareRecordReviewView,
)

app_name = "care"

urlpatterns = [
    path("", DailyCareRecordListView.as_view(), name="record_list"),
    path("nuevo/", DailyCareRecordCreateView.as_view(), name="record_create"),
    path("<int:pk>/", DailyCareRecordDetailView.as_view(), name="record_detail"),
    path(
        "<int:pk>/corregir/",
        DailyCareRecordCorrectView.as_view(),
        name="record_correct",
    ),
    path(
        "<int:pk>/revisar/",
        DailyCareRecordReviewView.as_view(),
        name="record_review",
    ),
    path(
        "planes/<int:resident_pk>/nuevo/",
        CarePlanCreateView.as_view(),
        name="plan_create",
    ),
    path(
        "planes/<int:pk>/editar/",
        CarePlanUpdateView.as_view(),
        name="plan_update",
    ),
    path(
        "planes/<int:pk>/cerrar/",
        CarePlanCloseView.as_view(),
        name="plan_close",
    ),
    path(
        "planes/<int:pk>/reactivar/",
        CarePlanReopenView.as_view(),
        name="plan_reopen",
    ),
]
