# Matriz de roles y permisos

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
| Enfermería | Enfermera/o responsable clínico | Mantiene la ficha clínica, los datos administrativos y los contactos. |
| Técnico/a | Técnico/a en enfermería | Consulta la ficha y, en etapas posteriores, registra cuidados e incidentes. |
| Cuidador/a | Cuidadores y cuidadores | Consulta la ficha y, en etapas posteriores, registra cuidados e incidentes. |
| Administración | Personal administrativo | Mantiene datos administrativos, contactos y usuarios; revisa auditoría. |

> Los roles Técnico/a y Cuidador/a tienen los mismos permisos en el incremento 1. Se mantienen separados para reportes y para futuras reglas más específicas.

## Permisos del incremento 1

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
| Ver auditoría | ✅ | ❌ | ❌ | ❌ | ✅ |
| Gestionar usuarios y roles | ❌ | ❌ | ❌ | ❌ | ✅ |
| Restablecer contraseña de otro usuario | ❌ | ❌ | ❌ | ❌ | ✅ |
| Acceder al admin técnico de Django | Solo superusuario | ❌ | ❌ | ❌ | ❌ |

**Nota:** la información clínica es de solo lectura para Dirección, Técnico/a, Cuidador/a y Administración. Solo Enfermería la modifica. Esto reduce el riesgo de cambios no clínicos en alergias o antecedentes.

## Permisos previstos para etapas posteriores

| Acción | Dirección | Enfermería | Técnico/a | Cuidador/a | Administración |
|---|:---:|:---:|:---:|:---:|:---:|
| Registrar cuidados diarios | ❌ | ✅ | ✅ | ✅ | ❌ |
| Leer registros diarios | ✅ | ✅ | ✅ | ✅ | ❌ |
| Reportar incidentes | ❌ | ✅ | ✅ | ✅ | ❌ |
| Revisar y cerrar incidentes | ✅ | ✅ | ❌ | ❌ | ❌ |
| Editar plan de cuidados | ❌ | ✅ | ❌ | ❌ | ❌ |
| Leer plan de cuidados | ✅ | ✅ | ✅ | ✅ | ❌ |
| Exportar reportes autorizados | ✅ | ✅ | ❌ | ❌ | ✅ |

Estas filas son una propuesta para discutir con el ELEAM antes de implementarlas; no están activas en el incremento 1.

## Reglas adicionales

1. **Nadie puede desactivar su propia cuenta** ni dejar el sistema sin al menos una persona con rol Administración activa.
2. **Los residentes no se eliminan:** se archivan y se pueden reactivar. La ficha archivada sigue disponible para consulta y auditoría.
3. **Los contactos se pueden eliminar** solo con permiso de Enfermería o Administración; la eliminación queda auditada con el snapshot anterior.
4. **Las contraseñas nunca se muestran ni se registran** en la auditoría. Solo se registra el hecho de que se cambiaron.
5. **La auditoría es de solo lectura** para Dirección y Administración; nadie la edita ni la elimina desde la aplicación.
6. **Un superusuario no reemplaza los roles:** si una persona usa el admin técnico, sus acciones también deben quedar registradas y revisarse.

## Verificación

La matriz se prueba automáticamente en `accounts/tests/`, `residents/tests/` y `audit/tests/`. Cada combinación crítica (rol × acción) debe tener al menos una prueba que confirme el acceso permitido o el rechazo con HTTP 403.

## Decisiones pendientes con el ELEAM

- [ ] ¿Dirección debe poder editar datos administrativos o solo leer?
- [ ] ¿Quién autoriza el ingreso y el egreso de un residente?
- [ ] ¿Administración necesita ver diagnósticos/antecedentes clínicos o solo alergias?
- [ ] ¿La auditoría debe ser visible para Enfermería sobre sus propios registros?
- [ ] ¿Se requiere doble aprobación para archivar una ficha?
- [ ] ¿Se usarán grupos de trabajo por turno además de los roles?
