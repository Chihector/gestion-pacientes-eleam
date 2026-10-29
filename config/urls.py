from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

admin.site.site_header = "ELEAM · Administración técnica"
admin.site.site_title = "ELEAM"
admin.site.index_title = "Administración técnica"

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "",
        RedirectView.as_view(pattern_name="core:dashboard", permanent=False),
        name="home",
    ),
    path("", include("accounts.urls")),
    path("", include("core.urls")),
    path("residentes/", include("residents.urls")),
    path("cuidados/", include("care.urls")),
    path("auditoria/", include("audit.urls")),
]
