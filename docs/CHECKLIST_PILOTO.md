# Checklist de preparación del piloto

Este checklist operacionaliza la etapa 5 de la [hoja de ruta](../HOJA_DE_RUTA.md). Su objetivo es evitar que el piloto comience solo porque “la aplicación funciona”: faltan validación institucional, revisión legal, respaldos y responsables.

**Estado general:** preparación técnica en curso. **No cargar datos reales** hasta completar los bloques 3, 4 y 5.

## 1. Brechas técnicas

- [x] Suite automatizada completa: **115 pruebas** pasan en PostgreSQL local (`pytest`).
- [x] Pruebas de la exportación CSV: permisos por rol, filtros y auditoría de la descarga.
- [x] Dependencias de producción declaradas en `requirements-prod.txt` (psycopg, gunicorn y waitress).
- [x] `python manage.py check` sin errores en desarrollo.
- [x] `python manage.py check --deploy` con configuración de producción: sin errores; la única advertencia era `security.W021` (HSTS preload), que se elimina al definir `SECURE_HSTS_PRELOAD=True` y asumir el compromiso del dominio.
- [x] Instalación limpia verificada en una copia temporal: `instalar.bat` creó la base, aplicó migraciones y cargó datos ficticios; el login respondió HTTP 200.
- [x] Respaldo y restauración SQLite verificados en una copia temporal (ver [Respaldo y restauración](RESPALDO_Y_RESTAURACION.md)).
- [ ] Probar `instalar.bat` en un PC Windows físico sin Python ni entorno virtual previo.
- [x] Conectar PostgreSQL 18 local y aplicar las migraciones, incluidas las de enfermedades y medicamentos.
- [ ] Preparar el despliegue PostgreSQL en staging: configurar HTTPS, estáticos y credenciales de entorno.
- [x] Probar respaldo y restauración completos sobre PostgreSQL (ensayo local 2026-11-04: dump → restauración en base de pruebas → `migrate --check` limpio → conteos idénticos; la base de pruebas se eliminó). Falta repetirlo en staging/producción.
- [ ] Ejecutar la suite y `check --deploy` en el entorno de staging antes de producción.

## 2. Decisión de despliegue

- [ ] Elegir entre copia local independiente por PC o instalación central compartida.
- [ ] Si es central: elegir proveedor, ubicación de datos, dominio, TLS y PostgreSQL administrado.
- [ ] Definir cómo se sirven los archivos estáticos (`collectstatic` y proxy/servidor).
- [ ] Definir presupuesto, disponibilidad, soporte y proceso de salida del proveedor.
- [ ] Designar a la persona responsable de operar el sistema y a quien tendrá acceso técnico.

## 3. Validación con el ELEAM

- [x] Validar los flujos con Dirección, Médico/a, Enfermera/o Jefe, Enfermería, Técnico/a, Cuidador/a y Administración. **Revisado: permisos actualizados**
- [ ] Confirmar roles y permisos de la [matriz de permisos](MATRIZ_PERMISOS.md).
- [ ] Validar categorías de cuidado, turnos (07–15 / 15–23 / 23–07) y campos clínicos.
- [ ] Acordar criterios y plazos de revisión de Enfermería.
- [ ] Acordar la ventana para corregir registros y el tratamiento de días anteriores.
- [ ] Validar campos, gravedad percibida, seguimiento y cierre de incidentes.
- [ ] Acordar indicadores agregados y quién puede consultarlos.
- [ ] Confirmar si se mantiene la exportación CSV de residentes y cómo se manejan los archivos descargados.
- [ ] Revisar la interfaz con al menos una persona de Enfermería y una de Administración.

## 4. Revisión legal y de seguridad

- [ ] Revisar obligaciones aplicables, incluidas las leyes 19.628, 20.584 y 21.719, con asesoría jurídica.
- [ ] Definir finalidad, base de licitud, información a residentes o representantes y derechos.
- [ ] Definir retención y eliminación de fichas, contactos, cuidados, incidentes y auditoría.
- [ ] Revisar contratos, ubicación y transferencias de datos con proveedores.
- [ ] Definir controles de acceso, bloqueo de pantalla y procedimiento ante pérdida de dispositivos.
- [ ] Definir respuesta ante incidentes de seguridad sin registrar datos clínicos en logs.
- [ ] Confirmar que los respaldos son cifrados y accesibles solo para personal autorizado.

## 5. Preparación operativa

- [ ] Designar responsables de cuentas, soporte, respaldos y respuesta ante incidentes.
- [ ] Capacitar al personal por rol.
- [ ] Definir un canal para reportar problemas y errores.
- [ ] Documentar un procedimiento manual de continuidad si falla el sistema o internet.
- [ ] Definir el grupo pequeño de residentes y usuarios del piloto, con autorización institucional.
- [ ] Pasar `DEMO_MODE=False`, eliminar datos ficticios y verificar que no queden credenciales demo.
- [ ] Acordar revisión semanal de errores, registros omitidos, facilidad de uso y tiempos.
- [ ] Mantener temporalmente el procedimiento actual como respaldo.

## Criterio de inicio del piloto

El piloto puede comenzar solo cuando existan, como mínimo:

1. Responsables institucionales y técnicos designados.
2. Permisos y flujos validados por el ELEAM.
3. Revisión legal y de seguridad completada.
4. Respaldo restaurable probado (incluido PostgreSQL si el piloto es central).
5. Capacitación realizada y procedimiento de continuidad acordado.
6. Datos ficticios eliminados y `DEMO_MODE=False`.

## Registro de avances

| Fecha | Avance | Evidencia |
|---|---|---|
| 2026-10-30 | Pruebas CSV y suite completa | 105 pruebas pasan en PostgreSQL local |
| 2026-10-30 | PostgreSQL local | Conexión a `127.0.0.1:5432`; migraciones aplicadas; `manage.py check` y `makemigrations --check --dry-run` correctos |
| 2026-11-04 | Migración de roles | `accounts.0002_alter_user_role` (roles `MEDICO` y `ENFERMERA_JEFE`) generada y aplicada; `makemigrations --check --dry-run` sin cambios |
| 2026-11-04 | Suite completa | 115 pruebas pasan en PostgreSQL local, incluida la prueba del endpoint `/health/` |
| 2026-11-04 | Humo del servidor | HTTP 200 en `/cuenta/login/`; 302 a login en `/`, `/admin/`, `/cuidados/`, `/incidentes/` |
| 2026-11-04 | Respaldo y restauración PostgreSQL | Dump en `respaldos/` (formato `pg_dump --format=custom`), restauración en base de pruebas `eleam_restore_test`, `migrate --check` limpio y conteos idénticos (7 usuarios, 9 residentes, 9 contactos, 7 cuidados); la base de pruebas se eliminó; el volcado de ensayo también se eliminó |
| 2026-11-04 | Cuentas demo | `seed_demo` crea 7 cuentas; se agregaron `medico@example.test` y `enfermera.jefe@example.test` |
| 2026-10-30 | Dependencias de producción | `requirements-prod.txt` validado con `pip --dry-run` |
| 2026-10-30 | Configuración de producción | `check --deploy` sin errores; advertencia opcional de HSTS preload documentada |
| 2026-10-30 | Instalación limpia | `instalar.bat` en copia temporal; login HTTP 200 |
| 2026-10-30 | Restauración SQLite | Integridad `ok`; restauración en copia limpia sin migraciones pendientes |
| 2026-10-30 | Prueba funcional en navegador | Login, roles, exportación CSV y auditoría; se detectó y corrigió un 500 al auditar una exportación, y se reverificó con `/auditoria/` en HTTP 200 mostrando el evento |
| Pendiente | Validación institucional, legal y operativa | Por agendar con el ELEAM |
