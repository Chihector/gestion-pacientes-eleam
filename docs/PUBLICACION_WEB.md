# Plan para publicar la aplicación web

La aplicación ya es una web Django, pero el despliegue web compartido **todavía no está preparado ni validado**. Una publicación permitirá que varios PCs usen el mismo sistema desde el navegador y una base común. No requiere convertirlo en una aplicación móvil o separar frontend y backend.

## Estado técnico verificado

Verificado el 2026-11-04 (la verificación del 2026-10-30 se conserva al pie):

- **115 pruebas automatizadas** pasan, incluida la prueba del endpoint `/health/` (200 si Django y la base de datos están operativas, 503 en caso contrario) para monitoreo sin autenticación.
- `requirements-prod.txt` declara `psycopg[binary]`, `gunicorn`, `waitress` y `whitenoise` (también está en `requirements.txt` porque `settings.py` carga el middleware).
- `python manage.py collectstatic --noinput` copia 135 archivos a `staticfiles/` (no versionado), y WhiteNoise los sirve correctamente con `DEBUG=False` detrás de Waitress (`/static/css/app.css` → HTTP 200 `text/css`).
- Prueba de humo con Waitress y `DEBUG=False` (secreto de un solo uso, `ALLOWED_HOSTS=127.0.0.1`): `/health/` → 200, `/` → 302 a `/panel/`, `/cuenta/login/` → 200, estáticos → 200. Con `SECURE_SSL_REDIRECT` (defecto), `check --deploy` no reporta ninguna advertencia (0 issues).
- `instalar.bat` fue verificada en una copia temporal (arranque y login HTTP 200) y el ensayo de respaldo/restauración PostgreSQL está documentado en [Respaldo y restauración](RESPALDO_Y_RESTAURACION.md).
- **Decisión tomada (2026-11-04):** el piloto central se hará en un servidor central con PostgreSQL administrado, HTTPS y acceso desde navegador; ya no se usará SQLite como base multiusuario ni `runserver` en producción. Pendientes: proveedor, dominio/TLS, estáticos en el hosting (WhiteNoise ya lo resuelve sin nginx; se puede mantener en el proxy si se prefiere), respaldos cifrados y validación institucional.

Verificación del 2026-10-30 (histórica):

- `python manage.py check --deploy` no reportaba errores con configuración de producción; solo quedaba la decisión opcional sobre HSTS preload.
- La instalación limpia con `instalar.bat` fue verificada en una copia temporal y el login respondió HTTP 200.
- Se probó un respaldo y restauración SQLite en una copia limpia.
- PostgreSQL 18 local se conectó correctamente y las migraciones están aplicadas.

## Recomendación

**Decisión adoptada (2026-11-04): el piloto se prepara sobre un servidor central.** Para un piloto con varios usuarios, usa un único entorno central alojado en una plataforma compatible con Django, con PostgreSQL administrado y HTTPS. Los usuarios entran desde el navegador; no se instala una base independiente en cada PC. No expongas `python manage.py runserver` ni uses SQLite como base multiusuario de producción.

Si no se desea alojar el sistema en internet, una segunda opción es un servidor dedicado dentro del ELEAM y acceso desde la red local. Esa modalidad aún requiere configurar el servidor de producción, HTTPS y controles de red; no basta con cambiar `127.0.0.1`.

## Pasos antes de publicar

1. **Validar el producto:** confirmar con el ELEAM flujos, campos, roles, permisos, exportación y responsabilidades operativas.
2. **Elegir responsable y alojamiento:** definir quién operará el sistema, quién tendrá acceso técnico, ubicación de datos, disponibilidad y soporte.
3. **Completar dependencias de producción:** ya se agregó `requirements-prod.txt` con `psycopg[binary]`, `gunicorn` y `waitress`. Elegir el servidor según el sistema operativo del hosting y validarlo en staging.
4. **Preparar una configuración de producción:** configurar `DJANGO_DEBUG=False`, `DJANGO_SECRET_KEY` robusta, `DEMO_MODE=False`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, credenciales PostgreSQL y correo mediante variables/secretos del proveedor. No subir secretos al repositorio.
5. **Servir la aplicación con HTTPS:** configurar dominio, certificado TLS y el servidor de aplicaciones elegido detrás de un proxy/servicio compatible. Activar la configuración de cookies seguras y HTTPS de Django.
6. **Publicar archivos estáticos:** ya está resuelto con WhiteNoise (`collectstatic --noinput` + `whitenoise.middleware.WhiteNoiseMiddleware` en `settings.py`; verificado con Waitress, `DEBUG=False`, HTTP 200 en `/static/css/app.css`). Si el hosting prefiere servir estáticos desde su proxy (nginx u otro), WhiteNoise puede retirarse sin tocar nada más.
7. **Verificar despliegue:** ejecutar migraciones en la base correcta, `python manage.py check --deploy` y las pruebas automatizadas en un entorno de staging antes de producción. La configuración actual pasa `check --deploy` sin errores; la única advertencia posible es `security.W021` (HSTS preload), que se resuelve con `SECURE_HSTS_PRELOAD=True` si el dominio asume ese compromiso.
8. **Proteger y operar los datos:** configurar respaldos cifrados, probar restauraciones, limitar accesos, documentar retención, monitorear disponibilidad (por ejemplo con `/health/`) y establecer respuesta ante incidentes sin registrar información clínica en logs técnicos. Ya se probó una restauración SQLite local y un ensayo completo de respaldo y restauración PostgreSQL en la instalación local (dump → restauración → verificación de conteos y `migrate --check`, 2026-11-04); falta probar el respaldo y la restauración PostgreSQL en un entorno de staging con datos del ELEAM. Ver [Respaldo y restauración](RESPALDO_Y_RESTAURACION.md).
9. **Hacer un piloto controlado:** empezar con un grupo pequeño autorizado, mantener el proceso actual como respaldo y ampliar solo tras revisar resultados.

## Comandos de referencia

```bash
# Dependencias de producción
python -m pip install -r requirements-prod.txt

# Estáticos y migraciones
python manage.py collectstatic --noinput
python manage.py migrate

# Servidor de aplicaciones (elegir uno)
gunicorn config.wsgi:application --bind 0.0.0.0:8000
waitress-serve --listen=0.0.0.0:8000 config.wsgi:application
```

No uses `python manage.py runserver` en producción. El proxy o servicio de hosting debe encargarse de HTTPS y de servir `STATIC_ROOT` si no se usa una capa específica para estáticos.

## No cargar datos reales todavía

La publicación técnica no acredita por sí sola el cumplimiento legal ni la preparación del ELEAM. Antes de importar información real, deben completarse la revisión legal y de seguridad, la validación institucional, capacitación, controles de acceso, respaldo restaurable y procedimiento de continuidad de la [hoja de ruta](../HOJA_DE_RUTA.md). No uses `seed_demo --force` ni las credenciales de demostración en producción.

## Decisión pendiente

- [x] Modalidad de despliegue (2026-11-04): **servidor central** con PostgreSQL administrado y HTTPS. Pendiente elegir si es hosting administrado en internet o servidor dedicado dentro del ELEAM y quién lo opera.
- [ ] Elegir entre hosting administrado en internet o servidor dedicado dentro del ELEAM.
- [ ] Definir responsables de operación, soporte, cuentas y respuesta ante incidentes.
- [ ] Acordar presupuesto, disponibilidad, retención y ubicación de respaldos/datos.
- [ ] Seleccionar y probar proveedor, PostgreSQL, servidor de aplicaciones y estrategia de estáticos en staging (WhiteNoise ya verificada localmente; gunicorn debe probarse en el hosting real, Windows usa waitress).
