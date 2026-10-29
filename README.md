# ELEAM · Gestión de residentes

Aplicación web para apoyar el registro y la consulta de información de residentes de un ELEAM chileno. Este repositorio contiene los **dos primeros incrementos funcionales**: inicio de sesión, usuarios y roles, auditoría, ficha de residente, contactos y registro diario de cuidados con plan, correcciones y revisión de Enfermería.

> **Privacidad:** usa solo datos ficticios en desarrollo, pruebas y demostraciones. No ingreses nombres, RUT, direcciones, teléfonos ni información de salud de personas reales. Antes de un piloto se deben validar los requisitos legales, de seguridad y de privacidad aplicables.

## Estado del proyecto

| Etapa | Estado |
|---|---|
| 1. Entender el problema | Documentada, pendiente de validación con el equipo |
| 2. Definir alcance y reglas | Documentada en `docs/` |
| 3. Prototipo navegable | Disponible en `prototipo/` (datos ficticios) |
| 4. MVP · incremento 1 | Implementado y probado técnicamente; pendiente de revisión con el equipo |
| 5. MVP · incremento 2 | Registros por turno, plan de cuidados, correcciones y revisión: implementado y probado; pendiente de validación con el equipo |
| 6. MVP · incremento 3 | Incidentes, informes y exportaciones: aún no implementado |

Documentos de referencia:

- [Hoja de ruta](HOJA_DE_RUTA.md)
- [Tecnologías recomendadas](TECNOLOGIAS.md)
- [Matriz de permisos](docs/MATRIZ_PERMISOS.md)
- [Historias de usuario de los incrementos 1 y 2](docs/HISTORIAS_DE_USUARIO.md)
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
- Datos ficticios de demostración.

## Qué incluye el incremento 2

- Bandeja de cuidados en `/cuidados/` con filtros por fecha, turno, categoría, residente o texto, pendientes de revisión y registros corregidos.
- Registro de cuidados por turno con residente, plan relacionado, fecha y hora, turno, categoría, descripción y observaciones.
- Los registros **no se editan ni se eliminan**: una corrección crea una versión nueva, exige un motivo y deja la versión anterior visible como `CORREGIDO`.
- Revisión de Enfermería para los registros marcados, con revisor, fecha y observaciones; la revisión y la corrección quedan en auditoría.
- Planes de cuidados por residente con necesidad, objetivo, acciones acordadas, responsable, fechas y observaciones.
- Cierre de planes con motivo obligatorio y reactivación auditada; no se eliminan.
- Pestaña “Cuidados” en la ficha del residente y panel “Cuidados de hoy” con registros y pendientes.
- Permisos: Enfermería gestiona planes, revisa y corrige cualquier registro; Técnico/a y Cuidador/a registran y corrigen sus propios registros; Dirección y Administración solo consultan.
- Datos ficticios adicionales y **67 pruebas automatizadas** en la suite completa.

**Fuera de alcance por ahora:** incidentes, informes, exportaciones, portal de familias, facturación, inventario, integraciones y aplicación móvil nativa. El sistema no diagnostica, no recomienda tratamientos, no define prioridades clínicas y no genera planes automáticamente.

## Stack

- Python 3.11+
- Django 5.2
- SQLite en desarrollo
- PostgreSQL en producción (configurable por variables de entorno)
- Plantillas Django + HTMX + Bootstrap 5
- Argon2 para el hash de contraseñas
- pytest y pytest-django para las pruebas

Los archivos de Bootstrap, Bootstrap Icons y HTMX están incluidos en `static/vendor/`, por lo que la interfaz funciona sin conexión a internet.

## Inicio rápido en Windows

Si el entorno ya está instalado, haz doble clic en **`iniciar.bat`**. El lanzador:

1. Verifica que exista el entorno virtual.
2. Crea y carga los datos ficticios si falta `db.sqlite3`.
3. Abre el navegador en `http://127.0.0.1:8000/cuenta/login/`.

Para detenerlo, presiona `Ctrl+C` o cierra la ventana negra. Si Windows muestra un aviso de SmartScreen, elige "Más información" → "Ejecutar de todas formas"; el archivo solo ejecuta el servidor local.

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
| `administracion@example.test` | Administración | Residentes, contactos, usuarios y auditoría; consulta cuidados |
| `direccion@example.test` | Dirección | Consultar fichas, cuidados y auditoría |
| `enfermeria@example.test` | Enfermería | Residentes, datos clínicos, planes, revisión y corrección de cuidados |
| `tecnico@example.test` | Técnico/a | Consultar fichas y registrar o corregir sus propios cuidados |
| `cuidador@example.test` | Cuidador/a | Consultar fichas y registrar o corregir sus propios cuidados |

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
| Ver planes y registros de cuidados | Sí | Sí | Sí | Sí | Sí |
| Registrar cuidados | No | Sí | Sí | Sí | No |
| Corregir registros | No | Sí (todos) | Sí (propios) | Sí (propios) | No |
| Gestionar y revisar cuidados | No | Sí | No | No | No |
| Ver auditoría completa | Sí | No | No | No | Sí |
| Gestionar usuarios | No | No | No | No | Sí |

La matriz detallada está en [docs/MATRIZ_PERMISOS.md](docs/MATRIZ_PERMISOS.md). Los permisos se validan en cada vista; los superusuarios técnicos pasan los controles.

## Auditoría y privacidad

- `AuditLog` es un registro append-only: desde la aplicación no se edita ni se elimina.
- Se guardan actor, fecha, IP, registro afectado y valores anterior/nuevo.
- No se guardan contraseñas ni hashes en la auditoría; los cambios de contraseña se registran como evento explícito.
- Las fichas no se eliminan: se archivan y se pueden reactivar.
- Los contactos se eliminan con confirmación y el evento conserva los datos anteriores.
- Los registros de cuidado no se editan ni se eliminan: una corrección crea una nueva versión, marca la anterior como corregida y conserva el motivo.
- Los planes de cuidado no se eliminan: se cierran con motivo y se pueden reactivar; ambas acciones quedan auditadas.
- La revisión de Enfermería guarda quién revisó, cuándo y qué observaciones dejó.
- Los planes y registros de cuidado son de solo lectura en el admin técnico de Django: se crean, corrigen y revisan desde la aplicación auditada.
- Los formularios de residentes, contactos y cuidados no permiten cargar archivos ni fotos en estos incrementos.
- La base de datos y los respaldos deben tratarse como información sensible en producción.
- No se deben enviar datos de residentes a herramientas de IA ni a servicios externos sin una evaluación previa.

## Pruebas

```powershell
pytest
```

La suite completa tiene **67 pruebas** y cubre, entre otros:

- Normalización y validación de RUT chileno.
- Creación de residentes con RUT válido y rechazo de duplicados.
- Permisos por rol en vistas administrativas, clínicas, de usuarios, cuidados y auditoría.
- Búsqueda, filtro de archivados y respuesta parcial HTMX.
- Archivado/reactivación y su registro en auditoría.
- Contacto principal único, creación y eliminación auditada.
- Inicio y cierre de sesión, contraseñas y protección de la propia cuenta.
- Registro de cambios con valores anterior/nuevo y ausencia de contraseñas.
- Registro de cuidados por turno, filtros de la bandeja y validaciones de fecha, residente y plan.
- Corrección con nueva versión, motivo obligatorio, conservación del original y bloqueo de doble corrección.
- Revisión de Enfermería solo para registros marcados, con revisor y fecha.
- Planes de cuidados, cierre con motivo, reactivación y bloqueo en fichas archivadas.
- Datos demo idempotentes y protección contra mezclar datos reales.

## Estructura del proyecto

```text
config/        Configuración y rutas raíz
core/          Panel, mixins de permisos y formularios base
accounts/      Usuario personalizado, roles, login y gestión de cuentas
residents/     Residentes, contactos, RUT y comando seed_demo
care/          Planes de cuidados, registros por turno, correcciones y revisión
audit/         Auditoría, middleware, signals y consulta de eventos
templates/     Plantillas Django
static/        CSS, JS y librerías front-end incluidas
docs/          Matriz de permisos, historias y modelo de datos
prototipo/     Prototipo estático navegable con datos ficticios
```

## Antes de un piloto con datos reales

1. Validar los flujos con Dirección, Enfermería, Técnicos, Cuidadores y Administración.
2. Validar con el equipo las categorías, los turnos, los campos clínicos, el criterio de revisión y el flujo de corrección antes de un piloto.
3. Revisar la matriz de permisos y las obligaciones legales de protección de datos.
4. Definir responsables de cuentas, respaldos, soporte y respuesta ante incidentes.
5. Configurar `DJANGO_DEBUG=False`, una `DJANGO_SECRET_KEY` robusta, HTTPS, HSTS y PostgreSQL administrado.
6. Desactivar `DEMO_MODE` y eliminar todos los datos ficticios.
7. Definir retención, respaldo y restauración; probar una restauración real.
8. Capacitar al personal y acordar un procedimiento manual de continuidad.
9. No cargar datos reales hasta completar estas verificaciones.

## Próximos incrementos

1. Incidentes, acciones tomadas y reportes básicos.
2. Exportaciones autorizadas, respaldos documentados y preparación del piloto.
3. Validación de los formularios de cuidados con el equipo y ajustes antes del piloto.

Este software es una base técnica. No reemplaza el criterio clínico ni constituye por sí solo un sistema listo para producción.
