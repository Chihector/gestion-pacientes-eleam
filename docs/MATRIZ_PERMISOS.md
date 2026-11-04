# Matriz de roles y permisos — incrementos 1, 2 y 3

## Principios

- **Mínimo privilegio:** cada rol recibe solo lo necesario para su trabajo.
- **Cuentas individuales:** no se comparten usuarios entre turnos ni entre personas.
- **Control en el servidor:** ocultar un botón no es un permiso; cada vista y acción se valida en el backend.
- **Separación de datos:** los datos administrativos y la información clínica se editan por separado.
- **Trazabilidad:** toda creación, modificación, archivado o desactivación queda en la auditoría.
- **Superusuario técnico:** existe para administración del sistema, no para el trabajo diario. Su uso debe ser excepcional y auditado.

## Roles del MVP

| Rol | Para quién | Propósito |
|---|---|---|
| Dirección | Dirección del establecimiento | Supervisión y lectura completa, incluida la auditoría. Edita datos administrativos. Ingreso/egreso. |
| Médico/a | Médico/a tratante | Edita datos administrativos y clínicos, gestiona enfermedades/medicamentos, ingreso/egreso, archiva fichas. |
| Enfermera/o Jefe | Enfermera/o jefe/superiora | Gestiona toda la clínica, cierra/reactiva planes, revisa cuidados, archiva fichas, ingreso/egreso. |
| Enfermería | Enfermera/o responsable clínico | Mantiene ficha clínica; gestiona enfermedades, medicamentos, planes y registra cuidados. No cierra planes. |
| Técnico/a | Técnico/a en enfermería | Consulta ficha, registra cuidados, edita observaciones y corrige sus propios registros. |
| Cuidador/a | Cuidadores y cuidadores | Consulta ficha, registra cuidados y corrige sus propios registros. |
| Administración | Personal administrativo | Mantiene datos administrativos, contactos y usuarios; revisa auditoría y consulta clínica completa. |

> Los roles Técnico/a y Cuidador/a tienen permisos similares pero diferenciados en observaciones. Grupos de trabajo por turno no se implementan.

## Permisos implementados (pendientes de validación institucional)

| Acción | Dirección | Médico | Enfermera Jefe | Enfermería | Técnico | Cuidador | Administración |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Iniciar y cerrar sesión | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Cambiar su propia contraseña | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Ver panel de inicio | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Buscar y listar residentes | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Ver ficha administrativa | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Ver información clínica completa | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Crear residente | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ | ✅ |
| Editar datos administrativos | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ |
| Editar información clínica | ❌ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| Registrar/editar enfermedades | ❌ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| Registrar/editar medicamentos | ❌ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| Crear/editar contactos | ❌ | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ |
| Archivar/reactivar residente | ❌ | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ |
| Ingreso/egreso (cambiar estado) | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Ver planes y cuidados | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Registrar un cuidado por turno | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ❌ |
| Corregir registro propio | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ❌ |
| Corregir cualquier registro | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Revisar registro marcado | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Editar observaciones cuidados | ❌ | ❌ | ✅ | ✅ | ✅ | ❌ | ❌ |
| Crear/editar planes cuidados | ❌ | ❌ | ✅ | ✅ | ❌ | ❌ | ❌ |
| Cerrar/reactivar plan | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Reportar incidente | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ❌ |
| Consultar reportes incidentes | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| Cerrar incidente | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Ver informes agregados incidentes | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Ver auditoría | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| Gestionar usuarios y roles | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| Restablecer contraseña otro usuario | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| Exportar nómina residentes (CSV) | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ | ✅ |

**Nota:** La información clínica es de solo lectura para Dirección, Técnico/a, Cuidador/a y Administración puede ver pero no editar. Solo Médico, Enfermera Jefe y Enfermería la modifican. Dirección puede editar datos administrativos y gestionar ingreso/egreso.

Administración conserva acceso a la auditoría general, pero los eventos detallados de incidentes se excluyen tanto de la auditoría como de la actividad reciente del panel para evitar que esa vía revele reportes a un rol sin acceso al módulo.

La aplicación implementa una exportación CSV de la nómina de residentes para Dirección, Enfermería y Administración. La descarga registra los filtros y el total exportado en auditoría. Los campos y el manejo de los archivos deben validarse con el ELEAM antes de usar datos reales. No se exportan cuidados ni incidentes.

## Permisos propuestos para etapas posteriores

| Acción | Dirección | Enfermería | Técnico/a | Cuidador/a | Administración |
|---|:---:|:---:|:---:|:---:|:---:|
| Exportar otros reportes autorizados | Por definir | Por definir | ❌ | ❌ | Por definir |

Las exportaciones adicionales requieren definir autorización, campos, límites y auditoría con el ELEAM.

## Reglas adicionales

1. **Nadie puede desactivar su propia cuenta** ni dejar el sistema sin al menos una persona con rol Administración activa.
2. **Los residentes no se eliminan:** se archivan y se pueden reactivar. La ficha archivada sigue disponible para consulta y auditoría.
3. **Los contactos se pueden eliminar** solo con permiso de Médico, Enfermera Jefe o Administración; la eliminación queda auditada con el snapshot anterior.
4. **Las contraseñas nunca se muestran ni se registran** en la auditoría. Solo se registra el hecho de que se cambiaron.
5. **La auditoría es de solo lectura** para Dirección y Administración; nadie la edita ni la elimina desde la aplicación.
6. **Un superusuario no reemplaza los roles:** si una persona usa el admin técnico, sus acciones también deben quedar registradas y revisarse. Los planes y registros de cuidado son de solo lectura en ese admin; las correcciones se hacen desde la aplicación.
7. **Los registros de cuidado no se editan ni se eliminan:** una corrección crea una nueva versión, exige un motivo y deja la anterior marcada como `CORREGIDO`. Solo el autor o Enfermera Jefe pueden corregir; Enfermera Jefe puede corregir cualquier registro vigente.
8. **La revisión de Enfermería solo aplica a registros marcados:** no se puede revisar un registro que no lo requiera, uno ya revisado o uno corregido. La revisión guarda revisor, fecha y observaciones. Solo Enfermera Jefe puede revisar.
9. **Los planes de cuidado los gestionan Enfermera Jefe y Enfermería:** solo Enfermera Jefe puede cerrarlos o reactivarlos con un motivo. No se eliminan. Una ficha archivada bloquea cambios en sus planes y registros.
10. **Ingreso/egreso y archivado:** solo Dirección, Médico, Enfermera Jefe y Administración (según acción) pueden gestionar cambios de estado.
11. **Observaciones en cuidados:** TENS puede editar observaciones/comentarios en registros de cuidado.

## Verificación

La matriz se prueba automáticamente en `accounts/tests.py`, `residents/tests.py`, `care/tests.py`, `incidents/tests.py` y `audit/tests.py`. Las operaciones clínicas sobre enfermedades y medicamentos son exclusivas de Enfermería (además de superusuarios técnicos); los demás roles autorizados pueden consultarlos. Las acciones de creación, edición y eliminación quedan auditadas.

Cada combinación crítica (rol × acción) debe tener al menos una prueba que confirme el acceso permitido o el rechazo con HTTP 403.

## Decisiones pendientes con el ELEAM

- [x] ✅ ¿Dirección debe poder editar datos administrativos o solo leer? **RESUELTO: Dirección puede editar**
- [x] ✅ ¿Quién autoriza el ingreso y el egreso de un residente? **RESUELTO: Dirección, Médico, Enfermera Jefe**
- [x] ✅ ¿Administración necesita ver diagnósticos/antecedentes clínicos o solo alergias? **RESUELTO: Puede ver todo clínico (solo lectura)**
- [x] ✅ ¿La auditoría debe ser visible para Enfermería sobre sus propios registros? **RESUELTO: No, solo Dirección y Administración**
- [x] ✅ ¿Se requiere doble aprobación para archivar una ficha? **RESUELTO: No, puede hacerlo Médico, Enfermera Jefe o Administración**
- [x] ✅ ¿Se usarán grupos de trabajo por turno además de los roles? **RESUELTO: No**
- [ ] ¿Las categorías de cuidado y los límites de turno (07–15, 15–23, 23–07) coinciden con la operación real?
- [ ] ¿Qué registros requieren revisión obligatoria de Enfermería y en qué plazo?
- [ ] ¿Se debe permitir corregir registros de días anteriores o solo del turno actual?
- [ ] ¿Los TENS pueden editar observaciones en cuidados? **RESUELTO: Sí**

