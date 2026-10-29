# ELEAM · Gestión de residentes

Aplicación web para apoyar el registro y la consulta de información de residentes de un ELEAM chileno. Este repositorio contiene el **primer incremento funcional**: inicio de sesión, usuarios y roles, auditoría, ficha de residente y contactos.

> **Privacidad:** usa solo datos ficticios en desarrollo, pruebas y demostraciones. No ingreses nombres, RUT, direcciones, teléfonos ni información de salud de personas reales. Antes de un piloto se deben validar los requisitos legales, de seguridad y de privacidad aplicables.

## Estado del proyecto

| Etapa | Estado |
|---|---|
| 1. Entender el problema | Documentada, pendiente de validación con el equipo |
| 2. Definir alcance y reglas | Documentada en `docs/` |
| 3. Prototipo navegable | Disponible en `prototipo/` (datos ficticios) |
| 4. MVP · incremento 1 | Implementado y probado técnicamente; pendiente de revisión con el equipo |
| Incrementos 2 y 3 | Registros diarios, plan de cuidados e incidentes: aún no implementados |

Documentos de referencia:

- [Hoja de ruta](HOJA_DE_RUTA.md)
- [Tecnologías recomendadas](TECNOLOGIAS.md)
- [Matriz de permisos](docs/MATRIZ_PERMISOS.md)
- [Historias de usuario del incremento 1](docs/HISTORIAS_DE_USUARIO.md)
- [Modelo de datos](docs/MODELO_DE_DATOS.md)

## Qué incluye el incremento 1

- Inicio y cierre de sesión con correo electrónico y contraseña.
- Cuentas individuales con cinco roles: Dirección, Enfermería, Técnico/a, Cuidador/a y Administración.
- Permisos comprobados en el servidor, no solo ocultando botones.
- Sesiones de 8 horas y expiración al cerrar el navegador.
- Panel con alertas de alergias, residentes sin contacto principal y actividad reciente.
- Búsqueda de residentes por nombre, RUT o habitación, con filtro de archivados y actualización parcial con HTMX.
- Ficha administrativa, información clínica relevante y contactos.
- Edición separada: Administración y Enfermería mantienen datos administrativos; solo Enfermería modifica alergias, antecedentes y observaciones.
- Archivado y reactivación de fichas sin eliminarlas.
- Contacto principal único por residente, con eliminación confirmada y auditada.
- Gestión de usuarios por Administración, con protección contra la desactivación de la propia cuenta.
- Auditoría de creación, modificación, archivado, reactivación, eliminación de contactos, desactivación de usuarios y cambios de contraseña.
- Datos ficticios de demostración y 43 pruebas automatizadas.

**Fuera de alcance por ahora:** registros diarios, plan de cuidados, incidentes, informes, exportaciones, portal de familias, facturación, inventario, integraciones y aplicación móvil nativa. El sistema no diagnostica, no recomienda tratamientos y no genera órdenes clínicas.

## Stack

- Python 3.11+
- Django 5.2
- SQLite en desarrollo
- PostgreSQL en producción (configurable por variables de entorno)
- Plantillas Django + HTMX + Bootstrap 5
- Argon2 para el hash de contraseñas
- pytest y pytest-django para las pruebas

Los archivos de Bootstrap, Bootstrap Icons y HTMX están incluidos en `static/vendor/`, por lo que la interfaz funciona sin conexión a internet.

## Instalación local

Recomendación: crear el entorno virtual **fuera de OneDrive** para evitar sincronizaciones y bloqueos de archivos.

### Windows PowerShell

```powershell
cd "C:\ruta\al\proyecto\Gestion pacientes eleam"

py -m venv C:\Users\<usuario>\.venvs\eleam
C:\Users\<usuario>\.venvs\eleam\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt

python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

Si PowerShell bloquea la activación del entorno:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
```

Abrir `http://127.0.0.1:8000/`.

### Linux / macOS

```bash
python3 -m venv ~/.venvs/eleam
source ~/.venvs/eleam/bin/activate
python -m pip install -r requirements-dev.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

## Cuentas de demostración

`seed_demo` crea estas cuentas ficticias. Todas usan la contraseña **`DemoEleam2026!`**:

| Correo | Rol | Puede hacer |
|---|---|---|
| `administracion@example.test` | Administración | Residentes, contactos, usuarios y auditoría |
| `direccion@example.test` | Dirección | Consultar fichas y auditoría |
| `enfermeria@example.test` | Enfermería | Residentes, contactos, datos administrativos y clínicos, auditoría no |
| `tecnico@example.test` | Técnico/a | Consultar fichas en modo lectura |
| `cuidador@example.test` | Cuidador/a | Consultar fichas en modo lectura |

El comando es idempotente, marca las fichas con `is_demo=True` y vuelve a dejar las contraseñas demo conocidas. Por seguridad:

- Se niega a ejecutarse si `DEMO_MODE` está desactivado.
- Se niega a mezclar datos ficticios con fichas que no estén marcadas como demo.
- `--force` existe solo para entornos controlados; **no lo uses con información real**.

```powershell
python manage.py seed_demo
```

Para volver a empezar desde cero en desarrollo:

```powershell
Remove-Item db.sqlite3
python manage.py migrate
python manage.py seed_demo
```

## Comandos útiles

```powershell
python manage.py check                 # Revisa la configuración
python manage.py migrate               # Aplica migraciones
python manage.py seed_demo             # Carga datos ficticios
python manage.py runserver             # Servidor de desarrollo
pytest                                 # Pruebas automatizadas
python manage.py collectstatic         # Prepara estáticos para producción
python manage.py createsuperuser       # Acceso al admin técnico de Django
```

El panel de administración técnica de Django está en `/admin/`. Las cuentas creadas por `seed_demo` no son `is_staff`; para usar ese panel crea un superusuario explícitamente.

## Variables de entorno

| Variable | Uso | Valor por defecto |
|---|---|---|
| `DJANGO_DEBUG` | Modo depuración | `True` |
| `DJANGO_SECRET_KEY` | Clave secreta; obligatoria con `DEBUG=False` | Solo una clave insegura de desarrollo |
| `ALLOWED_HOSTS` | Hosts permitidos, separados por coma | `localhost,127.0.0.1,[::1]` |
| `CSRF_TRUSTED_ORIGINS` | Orígenes confiables para CSRF | Vacío |
| `DEMO_MODE` | Muestra avisos de demostración | Igual a `DEBUG` |
| `POSTGRES_DB` | Activa PostgreSQL al definirla | SQLite si no existe |
| `POSTGRES_USER` | Usuario de PostgreSQL | Vacío |
| `POSTGRES_PASSWORD` | Contraseña de PostgreSQL | Vacío |
| `POSTGRES_HOST` | Host de PostgreSQL | `localhost` |
| `POSTGRES_PORT` | Puerto de PostgreSQL | `5432` |
| `SECURE_SSL_REDIRECT` | Redirige a HTTPS en producción | `True` |
| `SECURE_HSTS_SECONDS` | HSTS en producción | `31536000` |
| `USE_X_FORWARDED_PROTO` | Confía en `X-Forwarded-Proto` | `False` |
| `EMAIL_BACKEND` | Backend de correo | Consola en desarrollo |

Ejemplo para PostgreSQL en PowerShell:

```powershell
$env:POSTGRES_DB = "eleam"
$env:POSTGRES_USER = "eleam_app"
$env:POSTGRES_PASSWORD = "una-clave-larga-y-unica"
$env:POSTGRES_HOST = "localhost"
$env:POSTGRES_PORT = "5432"
python manage.py migrate
```

## Permisos resumidos

| Acción | Dirección | Enfermería | Técnico/a | Cuidador/a | Administración |
|---|---|---|---|---|---|
| Ver fichas | Sí | Sí | Sí | Sí | Sí |
| Crear/editar datos administrativos | No | Sí | No | No | Sí |
| Editar información clínica | No | Sí | No | No | No |
| Gestionar contactos | No | Sí | No | No | Sí |
| Archivar/reactivar fichas | No | Sí | No | No | Sí |
| Ver auditoría completa | Sí | No | No | No | Sí |
| Gestionar usuarios | No | No | No | No | Sí |

La matriz detallada está en [docs/MATRIZ_PERMISOS.md](docs/MATRIZ_PERMISOS.md). Los permisos se validan en cada vista; los superusuarios técnicos pasan los controles.

## Auditoría y privacidad

- `AuditLog` es un registro append-only: desde la aplicación no se edita ni se elimina.
- Se guardan actor, fecha, IP, registro afectado y valores anterior/nuevo.
- No se guardan contraseñas ni hashes en la auditoría; los cambios de contraseña se registran como evento explícito.
- Las fichas no se eliminan: se archivan y se pueden reactivar.
- Los contactos se eliminan con confirmación y el evento conserva los datos anteriores.
- Los formularios de residentes y contactos no permiten cargar archivos ni fotos en este incremento.
- La base de datos y los respaldos deben tratarse como información sensible en producción.
- No se deben enviar datos de residentes a herramientas de IA ni a servicios externos sin una evaluación previa.

## Pruebas

```powershell
pytest
```

La suite cubre, entre otros:

- Normalización y validación de RUT chileno.
- Creación de residentes con RUT válido y rechazo de duplicados.
- Permisos por rol en vistas administrativas, clínicas, de usuarios y auditoría.
- Búsqueda, filtro de archivados y respuesta parcial HTMX.
- Archivado/reactivación y su registro en auditoría.
- Contacto principal único, creación y eliminación auditada.
- Inicio y cierre de sesión, contraseñas y protección de la propia cuenta.
- Registro de cambios con valores anterior/nuevo y ausencia de contraseñas.
- Datos demo idempotentes y protección contra mezclar datos reales.

## Estructura del proyecto

```text
config/        Configuración y rutas raíz
core/          Panel, mixins de permisos y formularios base
accounts/      Usuario personalizado, roles, login y gestión de cuentas
residents/     Residentes, contactos, RUT y comando seed_demo
audit/         Auditoría, middleware, signals y consulta de eventos
templates/     Plantillas Django
static/        CSS, JS y librerías front-end incluidas
docs/          Matriz de permisos, historias y modelo de datos
prototipo/     Prototipo estático navegable con datos ficticios
```

## Antes de un piloto con datos reales

1. Validar los flujos con Dirección, Enfermería, Técnicos, Cuidadores y Administración.
2. Revisar la matriz de permisos y las obligaciones legales de protección de datos.
3. Definir responsables de cuentas, respaldos, soporte y respuesta ante incidentes.
4. Configurar `DJANGO_DEBUG=False`, una `DJANGO_SECRET_KEY` robusta, HTTPS, HSTS y PostgreSQL administrado.
5. Desactivar `DEMO_MODE` y eliminar todos los datos ficticios.
6. Definir retención, respaldo y restauración; probar una restauración real.
7. Capacitar al personal y acordar un procedimiento manual de continuidad.
8. No cargar datos reales hasta completar estas verificaciones.

## Próximos incrementos

1. Registro diario de cuidados y plan de cuidados acordado con el equipo.
2. Incidentes, acciones tomadas y reportes básicos.
3. Exportaciones autorizadas, respaldos documentados y preparación del piloto.

Este software es una base técnica. No reemplaza el criterio clínico ni constituye por sí solo un sistema listo para producción.
