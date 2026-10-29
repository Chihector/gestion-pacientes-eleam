from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .forms import AdminUserChangeForm, AdminUserCreationForm
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = AdminUserChangeForm
    add_form = AdminUserCreationForm
    ordering = ("email",)
    list_display = ("email", "first_name", "last_name", "role", "is_active", "is_staff")
    list_filter = ("role", "is_active", "is_staff")
    search_fields = ("email", "first_name", "last_name")
    readonly_fields = ("last_login", "created_at", "updated_at")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Datos personales", {"fields": ("first_name", "last_name")}),
        (
            "Rol y permisos",
            {
                "fields": (
                    "role",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Fechas", {"fields": ("last_login", "created_at", "updated_at")}),
    )
    add_fieldsets = (
        (
            "Nueva cuenta",
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "role",
                    "password1",
                    "password2",
                ),
            },
        ),
    )

    def has_delete_permission(self, request, obj=None):
        return False
