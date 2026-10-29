from django.contrib import admin

from .models import CarePlan, DailyCareRecord


@admin.register(CarePlan)
class CarePlanAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "resident",
        "status",
        "responsible",
        "start_date",
        "review_date",
    )
    list_filter = ("status", "start_date")
    search_fields = ("title", "resident__first_name", "resident__last_name")
    autocomplete_fields = ("resident", "responsible")
    readonly_fields = ("created_at", "updated_at", "created_by", "updated_by")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        return True


@admin.register(DailyCareRecord)
class DailyCareRecordAdmin(admin.ModelAdmin):
    list_display = (
        "recorded_at",
        "resident",
        "category",
        "shift",
        "status",
        "requires_nursing_review",
        "created_by",
    )
    list_filter = ("status", "shift", "category", "requires_nursing_review")
    search_fields = (
        "resident__first_name",
        "resident__last_name",
        "description",
    )
    autocomplete_fields = ("resident", "care_plan")
    readonly_fields = (
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
        "reviewed_by",
        "reviewed_at",
        "supersedes",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        return True
