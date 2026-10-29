from django.contrib import admin

from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "actor_repr", "action", "object_repr", "model_label")
    list_filter = ("action", "model_label")
    search_fields = ("actor_repr", "object_repr", "model_label", "object_id")
    readonly_fields = (
        "actor",
        "actor_repr",
        "action",
        "model_label",
        "object_id",
        "object_repr",
        "changes",
        "ip_address",
        "created_at",
    )
    date_hierarchy = "created_at"
    ordering = ("-created_at",)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
