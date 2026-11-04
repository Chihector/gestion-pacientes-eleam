# ELEAM · Gestión de residentes

Aplicación web para apoyar el registro y la consulta de información de residentes de un ELEAM chileno. Este repositorio contiene **tres incrementos funcionales**: inicio de sesión, usuarios y roles, auditoría, ficha de residente, cuidados con plan, correcciones y revisión de Enfermería, e incidentes con seguimiento e informes básicos.

> **Privacidad:** usa solo datos ficticios en desarrollo, pruebas y demostraciones. No ingreses nombres, RUT, direcciones, teléfonos ni información de salud de personas reales. Antes de un piloto se deben validar los requisitos legales, de seguridad y de privacidad aplicables.

## Estado del proyecto

| Etapa | Estado |
|---|---|
| 1. Entender el problema | Documentada, pendiente de validación con el equipo |
| 2. Definir alcance y reglas | Documentada en `docs/` |
| 3. Prototipo navegable | Disponible en `prototipo/` (datos ficticios) |
| 4. Construir el MVP | Incrementos funcionales 1, 2 y 3 implementados; 115 pruebas automatizadas |
| 5. Preparar el piloto (etapa actual) | Avances técnicos verificados; pendientes validación institucional, revisión legal/seguridad y operación |
| 6. Piloto controlado | Aún no iniciado |
| 7. Operación y mejora | Posterior al piloto |

Documentos de referencia:

- [Hoja de ruta](HOJA_DE_RUTA.md)
- [Tecnologías recomendadas](TECNOLOGIAS.md)
- [Matriz de permisos](docs/MATRIZ_PERMISOS.md)
- [Historias de usuario de los incrementos 1, 2 y 3](docs/HISTORIAS_DE_USUARIO.md)
- [Modelo de datos](docs/MODELO_DE_DATOS.md)
- [Instalación local en Windows](docs/INSTALACION_LOCAL.md)
- [Plan para publicación web](docs/PUBLICACION_WEB.md)
- [Checklist de preparación del piloto](docs/CHECKLIST_PILOTO.md)
- [Respaldo y restauración](docs/RESPALDO_Y_RESTAURACION.md)

## Qué incluye el incremento 1

- Inicio y cierre de sesión con correo electrónico y contraseña.
- Cuentas individuales con siete roles: Dirección, Médico/a, Enfermera/o Jefe, Enfermería, Técnico/a, Cuidador/a y Administración.
- Permisos comprobados en el servidor, no solo ocultando botones.
- Sesiones de 8 horas y expiración al cerrar el navegador.
- Panel con alertas de alergias, residentes sin contacto principal y actividad reciente.
- Búsqueda de residentes por nombre, RUT o habitación, con filtro de archivados y actualización parcial con HTMX.
- Exportación CSV de la nómina de residentes, con filtros aplicados y auditoría, cubierta por pruebas automatizadas; disponible para Dirección, Enfermera/o Jefe y Administración.
- Ficha administrativa, información clínica relevante y contactos.
- Edición separada: Dirección, Médico/a, Enfermera/o Jefe y Administración mantienen datos administrativos; Médico/a, Enfermera/o Jefe y Enfermería editan información clínica.
- Registro y edición posterior de enfermedades/condiciones y medicamentos por Médico/a, Enfermera/o Jefe y Enfermería; el resto de los roles autorizados puede consultarlos.
- Archivado y reactivación de fichas sin eliminarlas (Médico/a, Enfermera/o Jefe, Administración).
- Contacto principal único por residente, con eliminación confirmada y auditada.
- Gestión de usuarios por Administración, con protección contra la desactivación de la propia cuenta.
- Auditoría de creación, modificación, archivado, reactivación, eliminación de contactos, desactivación de usuarios y cambios de contraseña.
- Datos ficticios de demostración.

## Qué incluye el incremento 2

- Bandeja de cuidados en `/cuidados/` con filtros por fecha, turno, categoría, residente o texto, pendientes de revisión y registros corregidos.
- Registro de cuidados por turno con residente, plan relacionado, fecha y hora, turno, categoría, descripción y observaciones.
- Los registros **no se editan ni se eliminan**: una corrección crea una versión nueva, exige un motivo y deja la versión anterior visible como `CORREGIDO`.
- Revisión de Enfermería para los registros marcados, con revisor, fecha y observaciones; la revisión y la corrección quedan en auditoría. Solo Enfermera/o Jefe puede revisar.
- Planes de cuidados por residente con necesidad, objetivo, acciones acordadas, responsable, fechas y observaciones.
- Cierre de planes con motivo obligatorio y reactivación auditada; no se eliminan. Solo Enfermera/o Jefe puede cerrar/reactivar planes.
- Pestaña “Cuidados” en la ficha del residente y panel “Cuidados de hoy” con registros y pendientes.
- Permisos: Enfermera/o Jefe y Enfermería gestionan planes; Enfermera/o Jefe puede corregir y revisar cualquier registro; Técnico/a y Cuidador/a registran y corrigen sus propios registros y pueden editar observaciones; Dirección y Administración solo consultan.
- Datos ficticios adicionales y pruebas automatizadas de los incrementos 1 y 2.

## Qué incluye el incremento 3

- Registro confidencial de incidentes con residente, fecha, tipo, lugar, gravedad percibida, hechos, acciones inmediatas y notificaciones.
- Consulta de incidentes por Médico/a, Enfermera/o Jefe, Enfermería, Técnico/a, Cuidador/a y Dirección; Administración no accede al módulo ni a sus eventos detallados de auditoría.
- Cierre con seguimiento obligatorio por Dirección, Médico/a o Enfermera/o Jefe; el reporte original se conserva y el cierre queda auditado.
- Informes agregados por período, tipo, gravedad percibida y estado para Dirección, Médico/a y Enfermera/o Jefe. No exportan datos.
- El panel muestra incidentes abiertos a roles autorizados.

El flujo y los campos se basan en el prototipo y en los permisos propuestos; requieren validación con el ELEAM. El módulo no reemplaza el aviso inmediato, los protocolos institucionales ni la evaluación profesional.

La exportación CSV disponible se limita a la nómina de residentes. Los informes de incidentes no exportan datos y otras exportaciones aún requieren definición y autorización institucional. También quedan fuera de alcance el portal de familias, facturación, inventario, integraciones y aplicación móvil nativa. El sistema no diagnostica, no recomienda tratamientos, no define prioridades clínicas y no genera planes automáticamente.

## Stack

- Python 3.11+
- Django 5.2
- SQLite si no se configura `POSTGRES_DB`; PostgreSQL si se define (incluido el entorno local actual)
- PostgreSQL administrado recomendado para producción
- Plantillas Django + HTMX + Bootstrap 5
- Argon2 para el hash de contraseñas
- pytest y pytest-django para las pruebas

Los archivos de Bootstrap, Bootstrap Icons y HTMX están incluidos en `static/vendor/`, por lo que la interfaz funciona sin conexión a internet. Para producción, `requirements-prod.txt` agrega el controlador PostgreSQL y los servidores de aplicaciones (gunicorn en Linux, waitress en Windows).

## Inicio rápido en Windows

Para preparar una copia local en un PC nuevo, sigue [Instalación local](docs/INSTALACION_LOCAL.md). Ejecuta una vez **`instalar.bat`** y luego abre **`iniciar.bat`**. El lanzador:

1. Usa el entorno Python de `%USERPROFILE%\.venvs\eleam`, creado por el instalador.
2. Aplica las migraciones pendientes.
3. En una instalación nueva, carga datos ficticios.
4. Abre el navegador en `http://127.0.0.1:8000/cuenta/login/`.

Para detenerlo, presiona `Ctrl+C` o cierra la ventana negra. Si Windows muestra un aviso de SmartScreen, elige "Más información" → "Ejecutar de todas formas"; el archivo solo ejecuta el servidor local.

Esta modalidad mantiene datos separados por PC y solo escucha conexiones locales. Para compartir la aplicación entre varios PCs hay que preparar un despliegue central; consulta el [plan de publicación web](docs/PUBLICACION_WEB.md).

## Instalación local

Recomendación: crear el entorno virtual **fuera de OneDrive** para evitar sincronizaciones y bloqueos de archivos.

### Windows PowerShell

```powershell
cd "C:\ruta\al\proyecto\Gestion pacientes eleam"

py -3.11 -m venv C:\Users\<usuario>\.venvs\eleam
C:\Users\<usuario>\.venvs\eleam\Scripts\Activate.ps1
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
| `direccion@example.test` | Dirección | Consultar fichas, cuidados, incidentes e informes y auditoría; edita datos administrativos y gestiona ingreso/egreso |
| `medico@example.test` | Médico/a | Datos administrativos y clínicos, enfermedades/medicamentos, ingreso/egreso, archiva fichas, consulta incidentes e informes |
| `enfermera.jefe@example.test` | Enfermera/o Jefe | Gestiona la clínica: planes, revisión y corrección de cuidados, enfermedades/medicamentos, cierre y reactivación de planes, cierre/reactivación de fichas, incidentes e informes |
| `enfermeria@example.test` | Enfermería | Residentes, datos clínicos, planes y corrección de cuidados, enfermedades/medicamentos |
| `tecnico@example.test` | Técnico/a | Consultar fichas y registrar o corregir sus propios cuidados; reporta incidentes |
| `cuidador@example.test` | Cuidador/a | Consultar fichas y registrar o corregir sus propios cuidados; reporta incidentes |

El comando es idempotente, marca las fichas con `is_demo=True` y vuelve a dejar las contraseñas demo conocidas. Por seguridad:

- Se niega a ejecutarse si `DEMO_MODE` está desactivado.
- Se niega a mezclar datos ficticios con fichas que no estén marcadas como demo.
- `--force` existe solo para entornos controlados; **no lo uses con información real**.

```powershell
python manage.py seed_demo
```

Para reiniciar una instalación de desarrollo que use SQLite:

```powershell
Remove-Item db.sqlite3
python manage.py migrate
python manage.py seed_demo
```

Esto elimina los datos de esa base SQLite. No borres archivos para reiniciar una base PostgreSQL.

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
| Gestionar enfermedades y medicamentos | No | Sí | No | No | No |
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
- Las enfermedades y los medicamentos se pueden actualizar después de guardarlos; los cambios y eliminaciones quedan auditados. Solo Enfermería los gestiona desde la aplicación.
- La revisión de Enfermería guarda quién revisó, cuándo y qué observaciones dejó.
- Los planes y registros de cuidado son de solo lectura en el admin técnico de Django: se crean, corrigen y revisan desde la aplicación auditada.
- Los formularios de residentes, contactos y cuidados no permiten cargar archivos ni fotos en estos incrementos.
- La base de datos y los respaldos deben tratarse como información sensible en producción.
- No se deben enviar datos de residentes a herramientas de IA ni a servicios externos sin una evaluación previa.

## Pruebas

```powershell
python -m pytest
python -m pytest accounts/tests.py
python -m pytest accounts/tests.py::test_login_uses_email
```

La suite automatizada tiene actualmente **115 pruebas** y cubre, entre otros:

- Normalización y validación de RUT chileno.
- Creación de residentes con RUT válido y rechazo de duplicados.
- Permisos por rol en vistas administrativas, clínicas, de usuarios, cuidados y auditoría.
- Búsqueda, filtro de archivados y respuesta parcial HTMX.
- Permisos, filtros y auditoría de la exportación CSV de residentes.
- Renderizado de la auditoría con eventos de exportación sin registro individual.
- Archivado/reactivación y su registro en auditoría.
- Contacto principal único, creación y eliminación auditada.
- Inicio y cierre de sesión, contraseñas y protección de la propia cuenta.
- Registro de cambios con valores anterior/nuevo y ausencia de contraseñas.
- Registro de cuidados por turno, filtros de la bandeja y validaciones de fecha, residente y plan.
- Corrección con nueva versión, motivo obligatorio, conservación del original y bloqueo de doble corrección.
- Revisión de Enfermería solo para registros marcados, con revisor y fecha.
- Planes de cuidados, cierre con motivo, reactivación y bloqueo en fichas archivadas.
- Creación, edición posterior y eliminación auditada de enfermedades y medicamentos; pruebas de permisos clínicos, historial y fichas archivadas.
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
docs/          Matriz de permisos, historias, modelo de datos, checklist y respaldo
prototipo/     Prototipo estático navegable con datos ficticios
requirements-prod.txt  Dependencias de producción (PostgreSQL y servidor de aplicaciones)
```

## Antes de un piloto con datos reales

1. Validar los flujos con Dirección, Enfermería, Técnicos, Cuidadores y Administración.
2. Validar con el equipo las categorías, los turnos, los campos clínicos, el criterio de revisión y el flujo de corrección antes de un piloto.
3. Revisar la matriz de permisos y las obligaciones legales de protección de datos.
4. Definir responsables de cuentas, respaldos, soporte y respuesta ante incidentes.
5. Configurar `DJANGO_DEBUG=False`, una `DJANGO_SECRET_KEY` robusta, HTTPS, HSTS y PostgreSQL administrado.
6. Desactivar `DEMO_MODE` y eliminar todos los datos ficticios.
7. Definir retención, respaldo y restauración; ya se probó una restauración SQLite local y falta probar PostgreSQL.
8. Capacitar al personal y acordar un procedimiento manual de continuidad.
9. No cargar datos reales hasta completar estas verificaciones.

## Siguientes pasos: preparación del piloto

Los incrementos funcionales 1, 2 y 3 ya están implementados. El trabajo siguiente corresponde a la etapa 5 de `HOJA_DE_RUTA.md`, no a un nuevo incremento funcional:

1. Cerrar brechas técnicas: pruebas CSV (hechas), dependencias de producción (hechas), `check --deploy` (hecho) e instalación limpia y restauración SQLite (verificadas). Faltan PostgreSQL, HTTPS, estáticos y staging.
2. Probar `instalar.bat` en un PC Windows físico limpio, sin Python ni entorno virtual previo; verificar arranque, actualización y conservación de la base local.
3. Elegir el modo de uso: una copia local independiente por PC o una instalación central para que varios equipos compartan datos. Para el segundo caso, seguir [Plan para publicar la aplicación web](docs/PUBLICACION_WEB.md).
4. Validar con el ELEAM flujos y permisos; completar revisión legal y de seguridad, respaldos restaurables, capacitación y procedimiento de continuidad.
5. Iniciar un piloto controlado solo después de cumplir los criterios de preparación de la hoja de ruta y del [checklist del piloto](docs/CHECKLIST_PILOTO.md).

Este software es una base técnica. No reemplaza el criterio clínico ni constituye por sí solo un sistema listo para producción.
