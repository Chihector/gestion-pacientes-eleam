# Instalación local en Windows

Esta modalidad instala una copia para pruebas, demostraciones o uso local en **un solo PC**. Por defecto utiliza `db.sqlite3`; si se configura `POSTGRES_DB` en un archivo `.env`, Django utiliza PostgreSQL en su lugar. Las copias locales no comparten ni sincronizan datos entre equipos. Para que varias personas usen la misma información, revisa [Publicación web](PUBLICACION_WEB.md).

## Requisitos

- Windows 10 u 11.
- Python 3.11 instalado desde [python.org](https://www.python.org/downloads/windows/) con el lanzador `py`.
- Conexión a internet durante la primera instalación, para descargar Django y sus dependencias.

## Instalar y arrancar

1. Descarga el repositorio como ZIP o clónalo con Git.
2. Descomprime o ubica el proyecto en una carpeta local, por ejemplo `C:\ELEAM`. Evita OneDrive, carpetas de red y unidades sincronizadas para la base de datos.
3. Haz doble clic en `instalar.bat`. Crea el entorno virtual en `%USERPROFILE%\.venvs\eleam`, instala dependencias, aplica migraciones y carga datos ficticios si todavía no existe la base local.
4. Haz doble clic en `iniciar.bat` y abre `http://127.0.0.1:8000/cuenta/login/`.
5. Para detener el servidor, vuelve a la ventana negra y presiona `Ctrl+C`.

Las cuentas y contraseña de demostración están en la sección “Cuentas de demostración” del [README principal](../README.md). Son solo para datos ficticios. El comando de carga demo restaura las contraseñas conocidas; no lo uses con información real.

### Usar PostgreSQL en esta copia local

PostgreSQL se selecciona al definir `POSTGRES_DB`. Copia `.env.example` como `.env`, completa las variables de PostgreSQL con credenciales locales y confirma que el servicio esté disponible antes de ejecutar el instalador. El archivo `.env` está ignorado por Git: no lo compartas ni lo subas. Sin `POSTGRES_DB`, se usa SQLite.

La configuración local actual fue verificada con PostgreSQL 18 en `127.0.0.1:5432`; `residents.0002_disease_medication` está aplicada. Esto no equivale a preparar una instancia productiva ni a completar un ensayo de respaldo y restauración PostgreSQL.

## Verificación de instalación limpia (2026-10-30)

Se ejecutó `instalar.bat` sobre una copia temporal sin `db.sqlite3`, usando el entorno virtual existente:

- El instalador terminó con código 0 y creó `db.sqlite3`.
- Se aplicaron todas las migraciones y se cargaron 5 usuarios, 9 residentes, 9 contactos, 3 planes y 7 registros de cuidado ficticios.
- El servidor de desarrollo (`runserver`, el mismo comando que usa `iniciar.bat`) respondió HTTP 200 en `/cuenta/login/`.

**Pendiente:** repetir la prueba en un PC Windows físico sin Python ni entorno virtual previo, y comprobar una actualización conservando la base local.

## Verificación local (2026-11-04)

Sobre la instalación local con PostgreSQL 18 se confirmó: la migración `accounts.0002_alter_user_role` (roles `MEDICO` y `ENFERMERA_JEFE` en las opciones del campo) aplicada y `makemigrations --check --dry-run` sin cambios pendientes; la suite completa en **115 pruebas**; el servidor de desarrollo respondió HTTP 200 en `/cuenta/login/` y 302 (redirección a login) en `/`, `/admin/`, `/cuidados/` e `/incidentes/`; `seed_demo` agregó las cuentas ficticias `medico@example.test` y `enfermera.jefe@example.test` (total: 7 cuentas demo); y se ensayó un respaldo/restauración PostgreSQL completo (dump → restauración en una base de pruebas → `migrate --check` limpio → conteos idénticos; la base de pruebas se eliminó). Ver [Respaldo y restauración](RESPALDO_Y_RESTAURACION.md). La copia SQLite antigua se movió a `respaldos/db_2026-10-30_legado-sqlite.sqlite3`; la instalación usa PostgreSQL según `.env`.

## Actualizar la copia

1. Cierra el servidor con `Ctrl+C`.
2. Haz una copia protegida de `db.sqlite3` antes de actualizar.
3. Actualiza los archivos del proyecto sin reemplazar tu base local.
4. Ejecuta `instalar.bat` para instalar dependencias nuevas y aplicar migraciones; luego abre `iniciar.bat`.

No borres `db.sqlite3` para actualizar. Borrarla elimina los datos locales de esa instalación.

`iniciar.bat` aplica las migraciones pendientes antes de arrancar. Si una pantalla falla porque falta una tabla, ejecuta `python manage.py migrate` y revisa el estado con `python manage.py showmigrations`.

## Límites de esta modalidad

- La aplicación solo escucha en `127.0.0.1`: se accede desde el mismo PC.
- Cada copia mantiene sus propios usuarios y datos.
- No es un instalador ejecutable independiente: el PC requiere Python 3.11.
- El servidor incluido es el servidor de desarrollo de Django; esta instalación es para desarrollo/demostración y no debe exponerse a internet ni usarse como servidor productivo.
- Usa exclusivamente datos ficticios hasta completar las validaciones legales, de seguridad y operativas descritas en la hoja de ruta.

## Respaldo y restauración

Antes de actualizar, copia `db.sqlite3` a una carpeta protegida y verifica el archivo. El procedimiento completo, incluido PostgreSQL para un piloto central, está en [Respaldo y restauración](RESPALDO_Y_RESTAURACION.md).

Para ejecutar las pruebas automatizadas se necesitan las dependencias de desarrollo:

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest
```
