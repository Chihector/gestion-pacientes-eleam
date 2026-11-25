from django.contrib import admin
from django.contrib.staticfiles.storage import staticfiles_storage
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
    path("incidentes/", include("incidents.urls")),
    path("auditoria/", include("audit.urls")),
    # Chromium solicita /favicon.ico aunque la plantilla declare un SVG.
    path(
        "favicon.ico",
        RedirectView.as_view(url=staticfiles_storage.url("favicon.svg"), permanent=False),
        name="favicon",
    ),
]
