# Hoja de ruta

## Principios

- Diseñar junto con quienes registran y consultan la información durante sus turnos.
- Empezar por un alcance pequeño; no digitalizar todos los formularios de una vez.
- Evitar que el sistema sustituya el criterio profesional o genere órdenes clínicas.
- Usar datos ficticios durante el desarrollo y las pruebas.
- No iniciar un piloto con datos reales hasta revisar seguridad, privacidad, capacitación y continuidad operacional.

## Etapa 1: entender el problema

**Actividades**

- Conversar con dirección, enfermería, técnicos, cuidadores y administración.
- Observar, con autorización, cómo se hacen los registros durante distintos turnos.
- Listar formularios, planillas, libros y sistemas existentes.
- Identificar duplicación de registros, omisiones, demoras y dificultades para encontrar información.
- Acordar quién será responsable del producto y quién validará los flujos de cuidado.

**Entregables**

- Lista priorizada de problemas y necesidades.
- Mapa del proceso de ingreso, atención diaria, incidentes y egreso.
- Roles de usuario y tareas que necesita realizar cada rol.
- Decisión sobre qué queda fuera de la primera versión.

**Criterio para avanzar:** el personal confirma que los problemas y flujos descritos representan el trabajo real.

## Etapa 2: definir alcance y reglas

Definir para cada dato: quién lo registra, quién lo puede leer o corregir, cuándo se registra y cuánto tiempo debe conservarse.

**Alcance sugerido para el MVP**

- Usuarios, roles y acceso individual.
- Ficha del residente: identificación mínima necesaria, contactos, antecedentes relevantes y alergias.
- Plan de cuidados y registros diarios acordados con el equipo.
- Registro de incidentes y acciones tomadas.
- Historial de creación y modificación de registros, con usuario y fecha.
- Búsqueda y exportación limitada para tareas autorizadas.

**Dejar para una etapa posterior**

- Integraciones con otros sistemas, portal de familias, facturación e inventario avanzado.
- Alertas complejas, recomendaciones clínicas o cualquier función que decida tratamientos.
- Migración masiva del archivo histórico antes de validar el MVP.

**Entregables**

- Historias de usuario y reglas de negocio.
- Campos mínimos de cada formulario y ejemplos de reportes.
- Matriz de permisos por rol.
- Requisitos de privacidad, auditoría, respaldo y disponibilidad.

## Etapa 3: prototipo y validación

- Dibujar pantallas sencillas para teléfono, tablet y computador.
- Probar tareas concretas: encontrar un residente, revisar alergias, registrar un cuidado y reportar un incidente.
- Medir si el personal puede completar las tareas sin ayuda y en tiempo razonable.
- Revisar legibilidad, tamaño de controles y uso con conectividad intermitente.
- Ajustar los formularios antes de construir el sistema.

**Criterio para avanzar:** los representantes de cada rol aprueban los flujos y entienden qué información se guarda.

## Etapa 4: construir el MVP

Implementar en incrementos pequeños:

1. Inicio de sesión, usuarios, roles y auditoría. **Implementado.**
2. Ficha del residente y contactos. **Implementado.**
3. Registros diarios, plan de cuidados, correcciones y revisión de Enfermería. **Implementado y probado técnicamente; pendiente de validación con el equipo.**
4. Incidentes, consulta e informes básicos. **Implementado y probado técnicamente; pendiente de validación con el equipo.**
5. Pruebas automatizadas, respaldos y documentación operativa. **En curso: 115 pruebas pasan; PostgreSQL 18 local y sus migraciones verificados; instalación limpia y restauración SQLite y PostgreSQL (ensayo local) verificadas; publicación, respaldo/restauración PostgreSQL en staging y operación para piloto pendientes.**

Construir primero con datos ficticios. Revisar cada entrega con el personal del ELEAM. Registrar los cambios de forma que una corrección no borre silenciosamente el dato original.

## Etapa 5: pruebas y preparación del piloto

**Estado actual del proyecto:** los incrementos funcionales 1, 2 y 3 están implementados. El trabajo actual es verificar con el ELEAM las reglas y permisos, y completar la preparación legal, de seguridad y operación; no hay un incremento funcional 4 definido todavía.

**Progreso técnico verificado el 2026-10-30:** 114 pruebas pasaron en PostgreSQL 18 local; `manage.py check` no reportó problemas y `makemigrations --check --dry-run` no detectó cambios pendientes; las migraciones de enfermedades y medicamentos estaban aplicadas. La exportación CSV tiene pruebas de permisos, filtros y auditoría; `requirements-prod.txt` declara PostgreSQL y servidores de aplicaciones; `check --deploy` no arroja errores con configuración de producción (solo queda la decisión opcional de HSTS preload); `instalar.bat` funcionó en una copia limpia temporal y el login respondió HTTP 200; se probó un respaldo y restauración SQLite en una copia limpia; la prueba funcional en navegador confirmó permisos por rol, exportación CSV y auditoría, incluida la corrección de un 500 al auditar una exportación. El PostgreSQL local no equivale a un despliegue productivo ni a una restauración verificada en staging. El detalle está en el [checklist del piloto](docs/CHECKLIST_PILOTO.md).

**Progreso técnico verificado el 2026-11-04:** la migración `accounts.0002_alter_user_role` (roles `MEDICO` y `ENFERMERA_JEFE` en las opciones del campo `role`) se generó y aplicó; `makemigrations --check --dry-run` no detecta cambios pendientes; la suite completa tiene **115 pruebas** y todas pasan en PostgreSQL local; el servidor de desarrollo respondió HTTP 200 en `/cuenta/login/` y 302 a login en `/`, `/admin/`, `/cuidados/` e `/incidentes/`; `seed_demo` agregó las cuentas ficticias `medico@example.test` y `enfermera.jefe@example.test` (total: 7 cuentas demo); se agregó el endpoint `/health/` para monitoreo (200 operativo, 503 si la base de datos falla); se ensayó un respaldo y restauración PostgreSQL completo en una base de pruebas local (dump → restauración → `migrate --check` limpio → conteos idénticos al origen → base de pruebas eliminada); `collectstatic` copia 135 archivos y WhiteNoise los sirve con `DEBUG=False` (HTTP 200 en `/static/css/app.css` detrás de Waitress; `/` 302, login 200, `/health/` 200); `check --deploy` con configuración de producción no reporta ninguna advertencia; la documentación se actualizó y la copia SQLite antigua se resguardó en `respaldos/`. Se decidió preparar el piloto como **servidor central** (hosting por definir). Persiste el pendiente de ensayar respaldo/restauración PostgreSQL en staging y de completar validación institucional, legal y operativa.

- Probar permisos: cada rol ve y modifica solo lo autorizado.
- Probar casos normales y errores: campos incompletos, duplicados, correcciones y usuarios desactivados.
- [x] Probar `instalar.bat` en una copia limpia y comprobar el arranque y la actualización sin perder la base local. **Verificado en copia temporal; falta repetirlo en un PC Windows físico sin Python ni entorno virtual.**
- [x] Añadir o confirmar pruebas automatizadas de permisos, filtros y auditoría de la exportación CSV de residentes.
- Probar que el historial de cambios es consultable por personal autorizado.
- Revisar el alcance de la exportación CSV de residentes, sus campos, permisos y tratamiento de los archivos descargados.
- [x] Ensayar una restauración desde un respaldo SQLite.
- [x] Ensayar una restauración completa sobre PostgreSQL local (2026-11-04: dump → restauración en base de pruebas → verificación de conteos y `migrate --check`). **Falta repetirla en staging.**
- Preparar un procedimiento manual temporal si se cae el sistema o internet.
- [x] Decidir si el piloto usará un PC local por usuario o un servidor central para acceso compartido. **Decisión (2026-11-04): servidor central con PostgreSQL administrado y HTTPS; WhiteNoise sirve los estáticos; queda pendiente elegir entre hosting administrado o servidor dedicado en el ELEAM.**
- Capacitar a usuarios y definir un canal para reportar problemas.
- Validar los requisitos legales y de seguridad con personas competentes antes de cargar datos reales.

**Criterio para iniciar piloto:** hay responsables, permisos revisados, respaldo restaurable, capacitación y procedimiento de continuidad.

## Etapa 6: piloto controlado

- Elegir un grupo pequeño de residentes y usuarios, con autorización institucional.
- Mantener temporalmente el procedimiento actual como respaldo.
- Revisar semanalmente errores, registros omitidos, facilidad de uso y tiempos.
- Corregir problemas antes de ampliar el grupo.
- Ampliar gradualmente solo cuando el equipo confirme que el proceso es confiable.

## Etapa 7: operación y mejora

- Asignar responsables para soporte, usuarios, respaldos y actualizaciones.
- Revisar accesos y cuentas de personas que cambian de función o dejan el establecimiento.
- Practicar restauraciones y revisar incidentes de seguridad.
- Recoger sugerencias y priorizar mejoras según impacto en residentes y carga del equipo.
- Revisar periódicamente las obligaciones legales y las políticas de conservación y eliminación.

## Lista de decisiones pendientes

### Generales y de piloto

- [ ] Número de residentes, funcionarios y turnos que debe soportar el piloto.
- [ ] Dispositivos disponibles y calidad de internet en las áreas de atención.
- [x] Roles definitivos y permisos asociados. **REVISADO: Dirección, Médico/a, Enfermera/o Jefe, Enfermería, Técnico/a, Cuidador/a, Administración**
- [ ] Proveedor de alojamiento y ubicación de los datos.
- [ ] Requisitos de conservación, acceso, corrección y eliminación de datos.
- [ ] Responsable de soporte y respuesta ante incidentes.

### Funcionales y operacionales (cuidados e incidentes)

- [ ] Validación con el equipo de las categorías de cuidados acordadas.
- [ ] Validación de los rangos de turno (mañana 07–15, tarde 15–23, noche 23–07) según la rutina del ELEAM.
- [ ] Criterios y plazos de revisión obligatoria por parte de Enfermería.
- [ ] Ventana de tiempo permitida para que el autor corrija un registro antes del cierre de turno.
- [ ] Criterios de cierre y reapertura de planes de cuidados con el equipo clínico.
- [ ] Validar los campos, gravedad percibida, seguimiento, roles de acceso y cierre de incidentes.
- [ ] Acordar qué indicadores agregados son útiles y quién puede consultarlos.
- [ ] Confirmar con el ELEAM si se mantiene la exportación CSV de residentes y qué reglas operativas aplican a los archivos descargados.
