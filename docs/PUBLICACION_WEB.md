# Plan para publicar la aplicación web

La aplicación ya es una web Django, pero el despliegue web compartido **todavía no está preparado ni validado**. Una publicación permitirá que varios PCs usen el mismo sistema desde el navegador y una base común. No requiere convertirlo en una aplicación móvil o separar frontend y backend.

## Recomendación

Para un piloto con varios usuarios, usa un único entorno central alojado en una plataforma compatible con Django, con PostgreSQL administrado y HTTPS. Los usuarios entran desde el navegador; no se instala una base independiente en cada PC. No expongas `python manage.py runserver` ni uses SQLite como base multiusuario de producción.

Si no se desea alojar el sistema en internet, una segunda opción es un servidor dedicado dentro del ELEAM y acceso desde la red local. Esa modalidad aún requiere configurar el servidor de producción, HTTPS y controles de red; no basta con cambiar `127.0.0.1`.

## Pasos antes de publicar

1. **Validar el producto:** confirmar con el ELEAM flujos, campos, roles, permisos, exportación y responsabilidades operativas.
2. **Elegir responsable y alojamiento:** definir quién operará el sistema, quién tendrá acceso técnico, ubicación de datos, disponibilidad y soporte.
3. **Completar dependencias de producción:** `requirements.txt` aún no declara un controlador PostgreSQL ni un servidor WSGI/ASGI de producción. Elegirlos y añadirlos al proyecto antes del despliegue.
4. **Preparar una configuración de producción:** configurar `DJANGO_DEBUG=False`, `DJANGO_SECRET_KEY` robusta, `DEMO_MODE=False`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, credenciales PostgreSQL y correo mediante variables/secretos del proveedor. No subir secretos al repositorio.
5. **Servir la aplicación con HTTPS:** configurar dominio, certificado TLS y el servidor de aplicaciones elegido detrás de un proxy/servicio compatible. Activar la configuración de cookies seguras y HTTPS de Django.
6. **Publicar archivos estáticos:** ejecutar `python manage.py collectstatic --noinput` en el proceso de despliegue y configurar cómo se sirve `STATIC_ROOT`; la infraestructura actual no incluye un servidor dedicado de estáticos.
7. **Verificar despliegue:** ejecutar migraciones en la base correcta, `python manage.py check --deploy` y las pruebas automatizadas en un entorno de staging antes de producción.
8. **Proteger y operar los datos:** configurar respaldos cifrados, probar restauraciones, limitar accesos, documentar retención, monitorear disponibilidad y establecer respuesta ante incidentes sin registrar información clínica en logs técnicos.
9. **Hacer un piloto controlado:** empezar con un grupo pequeño autorizado, mantener el proceso actual como respaldo y ampliar solo tras revisar resultados.

## No cargar datos reales todavía

La publicación técnica no acredita por sí sola el cumplimiento legal ni la preparación del ELEAM. Antes de importar información real, deben completarse la revisión legal y de seguridad, la validación institucional, capacitación, controles de acceso, respaldo restaurable y procedimiento de continuidad de la [hoja de ruta](../HOJA_DE_RUTA.md). No uses `seed_demo --force` ni las credenciales de demostración en producción.

## Decisión pendiente

- [ ] Elegir entre hosting administrado en internet o servidor dedicado dentro del ELEAM.
- [ ] Definir responsables de operación, soporte, cuentas y respuesta ante incidentes.
- [ ] Acordar presupuesto, disponibilidad, retención y ubicación de respaldos/datos.
- [ ] Seleccionar y probar proveedor, PostgreSQL, servidor de aplicaciones y estrategia de estáticos en staging.
