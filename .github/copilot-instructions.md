# Instrucciones para Copilot

## Comandos

Instala dependencias de desarrollo y prepara la base local:

```powershell
python -m pip install -r requirements-dev.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

`seed_demo` crea datos ficticios y solo se ejecuta con `DEMO_MODE` habilitado. Para comprobar configuración y migraciones:

```powershell
python manage.py check
python manage.py makemigrations --check --dry-run
```

Pruebas con pytest:

```powershell
pytest
pytest accounts/tests.py
pytest accounts/tests.py::test_login_uses_email
```

No hay un comando de lint configurado en el repositorio. Los archivos estáticos del frontend ya están incluidos; no requieren una compilación aparte.

## Arquitectura

- El MVP funcional cubre los incrementos 1, 2 y 3. El proyecto está en la etapa de preparación del piloto según `HOJA_DE_RUTA.md`; no asumas que existe un incremento funcional 4 ni que las validaciones institucionales están completas.
- Es un monolito Django renderizado en servidor: `config/settings.py` configura las apps, middleware, base de datos, plantillas y estáticos; `config/urls.py` conecta las rutas de cada app.
- Las apps organizan el dominio: `accounts` contiene el usuario personalizado y roles; `residents` administra fichas y contactos; `care` contiene planes y registros por turno; `incidents` gestiona incidentes; `audit` registra cambios; `core` aporta panel y utilidades compartidas. Las vistas usan plantillas Django; HTMX actualiza parcialmente algunas listas.
- Usa siempre `settings.AUTH_USER_MODEL` o `get_user_model()` para referencias al usuario; el modelo personalizado se define en `accounts`.
- La autorización se aplica en el servidor mediante `RoleRequiredMixin` y `allowed_roles`, además de capacidades del usuario usadas por las vistas. Ocultar controles en una plantilla no sustituye la comprobación de permisos. Consulta `docs/MATRIZ_PERMISOS.md` antes de cambiar roles o accesos.
- La auditoría es transversal: `AuditContextMiddleware` establece usuario e IP después del middleware de autenticación; las señales de `audit` capturan cambios en modelos auditados, y `audit.services.log_action()` cubre eventos explícitos. Las operaciones de una petición usan transacciones por `ATOMIC_REQUESTS`.
- Mantén separados los formularios administrativos y clínicos de residentes. Los registros de cuidado no se editan ni eliminan: una corrección crea una nueva versión con motivo y conserva el original. Los planes se cierran/reactivan en vez de eliminarse; los residentes se archivan/reactivan. Conserva estas reglas de historial y auditoría.
- Para un cambio de dominio, revisa conjuntamente modelo, formulario, vista/ruta, plantilla, pruebas y migraciones de la app correspondiente. Las reglas detalladas están en `docs/MODELO_DE_DATOS.md` y `docs/HISTORIAS_DE_USUARIO.md`.

## Convenciones del proyecto

- Los identificadores y nombres de módulos siguen en inglés; las etiquetas, mensajes y textos de interfaz están en español. Mantén ese patrón y usa `TextChoices` para valores de dominio con opciones cerradas.
- Las fechas se almacenan con soporte de zona horaria y la zona local del sistema es `America/Santiago`.
- Las vistas son principalmente vistas genéricas de Django. Las listas que admiten HTMX seleccionan una plantilla parcial cuando `HX-Request` es `"true"`; conserva la respuesta completa para navegación normal.
- Las pruebas usan pytest-django, `pytest.ini` selecciona `config.settings` y `conftest.py` aporta fixtures comunes para usuarios por rol y residentes ficticios. Las pruebas de cada app suelen estar en `tests.py`.
- Usa exclusivamente datos ficticios en desarrollo, pruebas y demostraciones. No copies datos identificables o clínicos en fixtures, logs, cambios de instrucciones ni servicios externos de IA; el README y `TECNOLOGIAS.md` detallan las restricciones de privacidad.
