from django.contrib import admin

from .models import Contact, Resident


class ContactInline(admin.TabularInline):
    model = Contact
    extra = 0
    fields = ("name", "relationship", "phone", "email", "is_primary")
    readonly_fields = ()


@admin.register(Resident)
class ResidentAdmin(admin.ModelAdmin):
    list_display = (
        "last_name",
        "first_name",
        "rut",
        "room",
        "status",
        "is_active",
        "is_demo",
    )
    list_filter = ("is_active", "status", "is_demo", "health_insurance")
    search_fields = ("first_name", "last_name", "rut", "room")
    readonly_fields = ("created_at", "updated_at", "created_by", "updated_by")
    inlines = [ContactInline]
    fieldsets = (
        (
            "Identificación",
            {
                "fields": (
                    "is_demo",
                    "first_name",
                    "last_name",
                    "preferred_name",
                    "rut",
                    "birth_date",
                    "sex",
                )
            },
        ),
        (
            "Estadía",
            {
                "fields": (
                    "room",
                    "admission_date",
                    "status",
                    "health_insurance",
                    "is_active",
                )
            },
        ),
        (
            "Información clínica relevante",
            {"fields": ("allergies", "relevant_background", "clinical_notes")},
        ),
        (
            "Trazabilidad",
            {"fields": ("created_at", "updated_at", "created_by", "updated_by")},
        ),
    )

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("name", "resident", "relationship", "is_primary")
    list_filter = ("is_primary",)
    search_fields = ("name", "resident__first_name", "resident__last_name", "phone")
    readonly_fields = ("created_at", "updated_at", "created_by", "updated_by")

    def has_delete_permission(self, request, obj=None):
        return False
