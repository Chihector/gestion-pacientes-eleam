"""Ajustes de configuración para la suite automatizada de pruebas.

La suite usa SQLite en memoria para poder ejecutarse con un simple ``pytest``,
sin depender de un servidor PostgreSQL ni de credenciales locales. Las reglas
de negocio y los permisos se comprueban igual; la verificación concreta contra
PostgreSQL (staging) se ejecuta apuntando explícitamente a la configuración
de producción:

    DJANGO_SETTINGS_MODULE=config.settings pytest
"""

from config.settings import *  # noqa: F401,F403  (hereda toda la configuración)

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}
