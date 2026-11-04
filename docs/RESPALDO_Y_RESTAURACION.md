# Respaldo y restauración

Este documento define cómo respaldar y restaurar la base de datos del sistema. Es un requisito de la etapa 5 de la [hoja de ruta](../HOJA_DE_RUTA.md): **no se debe iniciar un piloto con datos reales sin un respaldo restaurable y una persona responsable de verificarlo**.

> **Privacidad:** los respaldos contienen datos personales y de salud. Deben tratarse como información sensible, cifrarse y almacenarse con acceso limitado. No se guardan en el repositorio, en correo personal ni en servicios sin evaluación.

## Reglas generales

1. Hacer un respaldo **antes de cada actualización** y antes de cambios masivos.
2. Verificar que el respaldo se pueda abrir y que tenga los datos esperados.
3. Probar una restauración completa en un entorno separado, nunca directamente sobre producción.
4. Cifrar los respaldos y limitar quién puede descargarlos.
5. Definir frecuencia, retención y ubicación con el ELEAM y con asesoría legal.
6. Registrar cada prueba de restauración: fecha, responsable, resultado y duración.
7. No usar `db.sqlite3` como base multiusuario de producción; para un piloto compartido se usa PostgreSQL.

## SQLite (desarrollo y copia local)

La instalación local usa `db.sqlite3`. Para respaldarla:

### Windows PowerShell

```powershell
# Detén el servidor con Ctrl+C antes de copiar.
$fecha = Get-Date -Format "yyyyMMdd_HHmmss"
$respaldo = "respaldos\db_$fecha.sqlite3"
Copy-Item db.sqlite3 $respaldo

# Verifica que el archivo no esté corrupto.
python -c "import sqlite3; c=sqlite3.connect(r'$respaldo'); print(c.execute('PRAGMA integrity_check').fetchone()[0])"
```

### Restauración

```powershell
# Detén el servidor.
Copy-Item db.sqlite3 "respaldos\db_antes_de_restaurar.sqlite3"
Copy-Item "respaldos\db_20261030_120000.sqlite3" db.sqlite3
python manage.py migrate --check
python manage.py runserver
```

`migrate --check` debe terminar sin migraciones pendientes. Si el respaldo es anterior a una actualización, ejecuta `python manage.py migrate` después de restaurarlo.

## PostgreSQL (producción)

Para un piloto central se usa PostgreSQL administrado. El respaldo debe hacerlo el proveedor o un proceso automatizado con `pg_dump`.

### Respaldo comprimido

```bash
pg_dump --format=custom --no-owner --no-privileges \
  --file=eleam_$(date +%Y%m%d_%H%M%S).dump \
  "$DATABASE_URL"
```

Si no se usa `DATABASE_URL`, definir `PGHOST`, `PGPORT`, `PGDATABASE`, `PGUSER` y `PGPASSWORD` mediante el gestor de secretos del proveedor.

### Restauración en un entorno de prueba

```bash
createdb eleam_restore_test
pg_restore --clean --if-exists --no-owner --no-privileges \
  --dbname=eleam_restore_test eleam_20261030_120000.dump
```

Luego apuntar una copia de la aplicación al entorno de prueba, ejecutar `python manage.py migrate --check` y verificar conteos y accesos antes de considerar válido el respaldo.

### Cifrado y almacenamiento

- Cifrar el archivo con `age`, `gpg` o el mecanismo del proveedor.
- Guardar copias en una ubicación distinta de la base principal.
- Definir retención (por ejemplo, diaria/semanal/mensual) con el ELEAM.
- Probar la restauración al menos una vez antes del piloto y luego con la periodicidad acordada.

## Registro de pruebas

| Fecha | Entorno | Acción | Resultado | Responsable |
|---|---|---|---|---|
| 2026-10-30 | SQLite local (copia temporal) | Respaldo, `PRAGMA integrity_check`, restauración en copia limpia y `migrate --check` | Correcto: integridad `ok`; 5 usuarios, 9 residentes, 9 contactos, 7 cuidados; sin migraciones pendientes | Verificación técnica del repositorio |
| 2026-11-04 | PostgreSQL 18 local (`respaldos/eleam_20261104_031913.dump`, formato custom) | `pg_dump` → `createdb eleam_restore_test` → `pg_restore --clean --if-exists` → `migrate --check` → conteos y `manage.py check` contra la copia → `dropdb` | Correcto: restauración sin errores; `migrate --check` limpio; conteos idénticos al origen (7 usuarios, 9 residentes, 9 contactos, 3 enfermedades, 3 medicamentos, 3 planes, 7 cuidados, 48 audit logs); volcado de ensayo eliminado tras verificar | Verificación técnica del repositorio |
| Pendiente | PostgreSQL de staging/producción | Respaldo cifrado y restauración completa | Pendiente de proveedor y responsables | Por definir |

## Pendientes antes del piloto

- [ ] Elegir proveedor de PostgreSQL y ubicación de los datos.
- [ ] Configurar respaldos automáticos y cifrados.
- [ ] Ejecutar una restauración completa en staging.
- [ ] Medir el tiempo de restauración y documentar el procedimiento.
- [ ] Definir retención, responsables y canal de respuesta ante incidentes.
- [ ] Confirmar que los respaldos no se incluyen en logs, repositorios ni copias informales.
