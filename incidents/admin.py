from django.contrib import admin

from .models import Incident


@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = (
        "occurred_at",
        "resident",
        "incident_type",
        "severity",
        "status",
        "created_by",
    )
    list_filter = ("status", "incident_type", "severity", "occurred_at")
    search_fields = ("resident__first_name", "resident__last_name", "description")
    readonly_fields = tuple(field.name for field in Incident._meta.fields)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
