from django.conf import settings


def app_settings(request):
    """Variables simples disponibles en todas las plantillas."""

    return {
        "demo_mode": settings.DEMO_MODE,
        "app_name": "ELEAM · Gestión de residentes",
    }
