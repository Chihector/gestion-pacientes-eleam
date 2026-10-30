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
| Dirección | Dirección del establecimiento | Supervisión y lectura completa, incluida la auditoría. No modifica fichas. |
| Enfermería | Enfermera/o responsable clínico | Mantiene la ficha clínica, los datos administrativos y los contactos; gestiona planes, revisa y corrige cuidados. |
| Técnico/a | Técnico/a en enfermería | Consulta la ficha, registra cuidados y corrige sus propios registros. |
| Cuidador/a | Cuidadores y cuidadores | Consulta la ficha, registra cuidados y corrige sus propios registros. |
| Administración | Personal administrativo | Mantiene datos administrativos, contactos y usuarios; revisa auditoría y consulta cuidados. |

> Los roles Técnico/a y Cuidador/a tienen los mismos permisos en estos incrementos. Se mantienen separados para reportes y para futuras reglas más específicas.

## Permisos implementados (pendientes de validación institucional)

| Acción | Dirección | Enfermería | Técnico/a | Cuidador/a | Administración |
|---|:---:|:---:|:---:|:---:|:---:|
| Iniciar y cerrar sesión | ✅ | ✅ | ✅ | ✅ | ✅ |
| Cambiar su propia contraseña | ✅ | ✅ | ✅ | ✅ | ✅ |
| Ver panel de inicio | ✅ | ✅ | ✅ | ✅ | ✅ |
| Buscar y listar residentes | ✅ | ✅ | ✅ | ✅ | ✅ |
| Ver ficha administrativa | ✅ | ✅ | ✅ | ✅ | ✅ |
| Ver información clínica relevante (alergias y antecedentes) | ✅ | ✅ | ✅ | ✅ | ✅ |
| Crear residente | ❌ | ✅ | ❌ | ❌ | ✅ |
| Editar datos administrativos del residente | ❌ | ✅ | ❌ | ❌ | ✅ |
| Editar información clínica | ❌ | ✅ | ❌ | ❌ | ❌ |
| Crear, editar y eliminar contactos | ❌ | ✅ | ❌ | ❌ | ✅ |
| Archivar o reactivar residente | ❌ | ✅ | ❌ | ❌ | ✅ |
| Ver planes y registros de cuidados | ✅ | ✅ | ✅ | ✅ | ✅ |
| Registrar un cuidado por turno | ❌ | ✅ | ✅ | ✅ | ❌ |
| Corregir un registro | ❌ | ✅ (todos) | ✅ (propios) | ✅ (propios) | ❌ |
| Revisar un registro marcado | ❌ | ✅ | ❌ | ❌ | ❌ |
| Crear o editar planes de cuidados | ❌ | ✅ | ❌ | ❌ | ❌ |
| Cerrar o reactivar un plan | ❌ | ✅ | ❌ | ❌ | ❌ |
| Reportar un incidente | ❌ | ✅ | ✅ | ✅ | ❌ |
| Consultar reportes de incidentes | ✅ | ✅ | ✅ | ✅ | ❌ |
| Cerrar un incidente con seguimiento | ✅ | ✅ | ❌ | ❌ | ❌ |
| Ver informes agregados de incidentes | ✅ | ✅ | ❌ | ❌ | ❌ |
| Ver auditoría | ✅ | ❌ | ❌ | ❌ | ✅ |
| Gestionar usuarios y roles | ❌ | ❌ | ❌ | ❌ | ✅ |
| Restablecer contraseña de otro usuario | ❌ | ❌ | ❌ | ❌ | ✅ |
| Acceder al admin técnico de Django | Solo superusuario | ❌ | ❌ | ❌ | ❌ |
| Exportar nómina de residentes (CSV) | ✅ | ✅ | ❌ | ❌ | ✅ |

**Nota:** la información clínica es de solo lectura para Dirección, Técnico/a, Cuidador/a y Administración. Solo Enfermería la modifica. Esto reduce el riesgo de cambios no clínicos en alergias o antecedentes.

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
3. **Los contactos se pueden eliminar** solo con permiso de Enfermería o Administración; la eliminación queda auditada con el snapshot anterior.
4. **Las contraseñas nunca se muestran ni se registran** en la auditoría. Solo se registra el hecho de que se cambiaron.
5. **La auditoría es de solo lectura** para Dirección y Administración; nadie la edita ni la elimina desde la aplicación.
6. **Un superusuario no reemplaza los roles:** si una persona usa el admin técnico, sus acciones también deben quedar registradas y revisarse. Los planes y registros de cuidado son de solo lectura en ese admin; las correcciones se hacen desde la aplicación.
7. **Los registros de cuidado no se editan ni se eliminan:** una corrección crea una nueva versión, exige un motivo y deja la anterior marcada como `CORREGIDO`. Solo el autor o Enfermería pueden corregir; Enfermería puede corregir cualquier registro vigente.
8. **La revisión de Enfermería solo aplica a registros marcados:** no se puede revisar un registro que no lo requiera, uno ya revisado o uno corregido. La revisión guarda revisor, fecha y observaciones.
9. **Los planes de cuidado los gestiona solo Enfermería:** se cierran con un motivo de al menos 10 caracteres y se pueden reactivar; no se eliminan. Una ficha archivada bloquea cambios en sus planes y registros.

## Verificación

La matriz se prueba automáticamente en `accounts/tests.py`, `residents/tests.py`, `care/tests.py`, `incidents/tests.py` y `audit/tests.py`. Cada combinación crítica (rol × acción) debe tener al menos una prueba que confirme el acceso permitido o el rechazo con HTTP 403.

## Decisiones pendientes con el ELEAM

- [ ] ¿Dirección debe poder editar datos administrativos o solo leer?
- [ ] ¿Quién autoriza el ingreso y el egreso de un residente?
- [ ] ¿Administración necesita ver diagnósticos/antecedentes clínicos o solo alergias?
- [ ] ¿La auditoría debe ser visible para Enfermería sobre sus propios registros?
- [ ] ¿Se requiere doble aprobación para archivar una ficha?
- [ ] ¿Se usarán grupos de trabajo por turno además de los roles?
- [ ] ¿Las categorías de cuidado y los límites de turno (07–15, 15–23, 23–07) coinciden con la operación real?
- [ ] ¿Qué registros requieren revisión obligatoria de Enfermería y en qué plazo?
- [ ] ¿Se debe permitir corregir registros de días anteriores o solo del turno actual?
- [ ] ¿Quién puede cerrar un plan además de Enfermería y qué motivo mínimo se exige?
