# Historias de usuario — Incrementos 1 y 2

Este documento define el alcance funcional de los dos primeros incrementos. Está escrito para validarlo con el equipo del ELEAM antes de ampliarlo. Todas las pruebas y demos usan **datos ficticios**.

## Alcance del incremento 1

Incluye:

- Inicio de sesión con cuentas individuales, roles y cierre de sesión.
- Gestión de usuarios por parte de Administración.
- Auditoría de creación, modificación, archivado, desactivación y cambio de contraseña.
- Búsqueda y consulta de residentes.
- Ficha administrativa, información clínica relevante (alergias y antecedentes) y contactos.
- Creación, edición, archivado y reactivación de residentes.
- Datos ficticios de demostración y pruebas automatizadas.

No incluye todavía:

- Incidentes e informes (incremento 3).
- Portal de familias, facturación, inventario, integraciones o aplicación móvil nativa.
- Alertas automáticas, recomendaciones clínicas o cualquier función que decida tratamientos.
- Migración de registros históricos.

## Alcance del incremento 2

Incluye:

- Registro de cuidados por turno, con fecha y hora, turno, categoría, descripción y observaciones.
- Bandeja de cuidados con filtros por fecha, turno, categoría, residente o texto, pendientes de revisión y registros corregidos.
- Corrección mediante una nueva versión: el registro original no se borra ni se sobrescribe.
- Revisión de Enfermería para registros marcados, con revisor, fecha y observaciones.
- Planes de cuidados acordados por Enfermería, con cierre motivado y reactivación auditada.
- Pestaña de cuidados en la ficha y resumen en el panel de inicio.
- Datos ficticios y pruebas automatizadas.

No incluye todavía:

- Diagnósticos, recomendaciones automáticas, prioridades clínicas ni generación de planes por IA.
- Firma electrónica avanzada, receta electrónica o integración con dispositivos clínicos.
- Incidentes, informes, exportaciones y portal de familias.

## Actores

- **Dirección:** supervisa, consulta cuidados y revisa auditoría.
- **Enfermería:** mantiene la ficha clínica y administrativa, gestiona planes, revisa y corrige registros de cuidados.
- **Técnico/a y Cuidador/a:** consultan la ficha, registran cuidados y corrigen sus propios registros.
- **Administración:** gestiona datos administrativos, contactos y usuarios; consulta cuidados y auditoría.
- **Superusuario técnico:** mantiene el sistema; no es un rol de trabajo diario.

## Historias

### US-01 — Iniciar sesión con cuenta individual

**Como** persona del equipo **quiero** entrar con mi correo y contraseña **para** acceder solo a lo que me corresponde.

**Criterios de aceptación**

- [ ] El acceso usa correo electrónico y contraseña; no hay usuario compartido.
- [ ] Una cuenta desactivada no puede iniciar sesión.
- [ ] La sesión expira a las 8 horas o al cerrar el navegador.
- [ ] El cierre de sesión se hace con POST y no queda una sesión activa.
- [ ] Los errores no revelan si el correo existe o no.
- [ ] La pantalla funciona en teléfono, tablet y computador.

**Prioridad:** alta.

### US-02 — Cambiar mi contraseña

**Como** usuario **quiero** cambiar mi contraseña **para** mantener mi cuenta protegida.

**Criterios de aceptación**

- [ ] Se solicita la contraseña actual.
- [ ] La nueva contraseña cumple la política mínima (10 caracteres, no común, no numérica).
- [ ] El cambio queda registrado en auditoría sin guardar la contraseña ni su hash.
- [ ] La sesión continúa activa después del cambio.

**Prioridad:** alta.

### US-03 — Gestionar usuarios y roles

**Como** Administración **quiero** crear, editar y desactivar cuentas **para** incorporar y retirar personal de forma controlada.

**Criterios de aceptación**

- [ ] Solo Administración puede entrar a la gestión de usuarios.
- [ ] Se puede crear una cuenta con correo único, nombre, apellido, rol y contraseña inicial.
- [ ] Se puede cambiar el rol y desactivar una cuenta sin eliminarla.
- [ ] No se puede desactivar la propia cuenta.
- [ ] No se puede dejar el sistema sin una cuenta activa con rol Administración.
- [ ] Cada cambio queda auditado con actor y fecha.
- [ ] Las contraseñas se almacenan con el algoritmo seguro de Django y nunca se muestran.

**Prioridad:** alta.

### US-04 — Restablecer la contraseña de otra persona

**Como** Administración **quiero** asignar una contraseña temporal **para** ayudar a alguien que no puede entrar.

**Criterios de aceptación**

- [ ] Solo Administración puede hacerlo.
- [ ] Se pide la nueva contraseña dos veces y se valida la política.
- [ ] El cambio se registra en auditoría como acción separada, sin guardar la contraseña.
- [ ] Se recomienda a la persona cambiar la contraseña al ingresar.

**Prioridad:** media.

### US-05 — Consultar el panel de inicio

**Como** usuario **quiero** ver un resumen del establecimiento **para** orientarme al comenzar el turno.

**Criterios de aceptación**

- [ ] Muestra cantidad de residentes activos y residentes con alergias registradas.
- [ ] Muestra los últimos residentes incorporados y alertas de alergias.
- [ ] Ofrece accesos directos según el rol.
- [ ] No muestra información de auditoría a quien no tiene permiso.
- [ ] Se adapta a pantallas pequeñas.

**Prioridad:** media.

### US-06 — Buscar residentes

**Como** miembro del equipo **quiero** buscar por nombre, RUT o habitación **para** encontrar una ficha rápidamente durante el turno.

**Criterios de aceptación**

- [ ] La búsqueda es parcial y no distingue mayúsculas ni tildes básicas.
- [ ] Se puede filtrar por estado (activo, hospitalizado, egresado) y por archivados.
- [ ] Los resultados muestran nombre, RUT, habitación, edad, estado y alerta de alergia.
- [ ] Sin JavaScript la búsqueda funciona con el botón "Buscar".
- [ ] Con HTMX la lista se actualiza sin recargar la página.
- [ ] La lista se pagina y no expone datos a usuarios anónimos.

**Prioridad:** alta.

### US-07 — Ver la ficha de un residente

**Como** miembro del equipo **quiero** ver identificación, contactos y antecedentes relevantes **para** prestar un cuidado seguro y coordinado.

**Criterios de aceptación**

- [ ] Se ven datos administrativos, alergias, antecedentes relevantes y contactos.
- [ ] Las alergias se destacan visualmente.
- [ ] Se ve quién creó y actualizó por última vez la ficha.
- [ ] Los botones de edición solo aparecen para roles autorizados.
- [ ] La ficha archivada se muestra como archivada y no se puede editar hasta reactivarla.
- [ ] Los datos de demostración llevan una marca visible "DEMO".

**Prioridad:** alta.

### US-08 — Crear un residente

**Como** Enfermería o Administración **quiero** registrar el ingreso **para** iniciar la ficha del residente.

**Criterios de aceptación**

- [ ] El RUT es obligatorio, válido y único.
- [ ] La fecha de nacimiento no puede ser futura y la fecha de ingreso no puede ser anterior al nacimiento.
- [ ] Se registran datos mínimos: nombre, apellido, RUT, nacimiento, habitación, ingreso, previsión y estado.
- [ ] La información clínica se completa después, solo por Enfermería.
- [ ] La creación queda auditada con el usuario y la fecha.
- [ ] Un rol no autorizado recibe HTTP 403.

**Prioridad:** alta.

### US-09 — Editar datos administrativos

**Como** Enfermería o Administración **quiero** corregir identificación, habitación, previsión o estado **para** mantener la ficha vigente.

**Criterios de aceptación**

- [ ] Solo se editan campos administrativos en este formulario.
- [ ] El RUT sigue siendo único.
- [ ] Los cambios quedan auditados con valor anterior y nuevo.
- [ ] No se puede editar una ficha archivada sin reactivarla.
- [ ] Técnico/a, Cuidador/a y Dirección reciben HTTP 403 si intentan editar.

**Prioridad:** alta.

### US-10 — Editar información clínica relevante

**Como** Enfermería **quiero** actualizar alergias y antecedentes **para** que el resto del equipo cuide con información correcta.

**Criterios de aceptación**

- [ ] Solo Enfermería puede editar alergias, antecedentes y observaciones clínicas.
- [ ] El formulario advierte que no se deben registrar diagnósticos innecesarios ni datos de terceros.
- [ ] Cada cambio queda auditado con valor anterior y nuevo.
- [ ] Los demás roles ven la información en modo lectura.

**Prioridad:** alta.

### US-11 — Gestionar contactos

**Como** Enfermería o Administración **quiero** mantener los contactos del residente **para** comunicarnos con quien corresponda.

**Criterios de aceptación**

- [ ] Se puede crear, editar y eliminar un contacto con nombre, parentesco, teléfono, correo y notas.
- [ ] Solo puede haber un contacto principal por residente; al marcarlo se desmarca el anterior.
- [ ] Se muestra quién es el contacto principal en la ficha.
- [ ] La eliminación pide confirmación y queda auditada con los datos anteriores.
- [ ] Técnico/a, Cuidador/a y Dirección no pueden modificar contactos.

**Prioridad:** alta.

### US-12 — Archivar y reactivar residentes

**Como** Enfermería o Administración **quiero** archivar una ficha cuando la persona egresa **para** conservar el historial sin mezclarla con los residentes activos.

**Criterios de aceptación**

- [ ] Archivar no elimina la ficha ni sus contactos.
- [ ] La ficha archivada deja de aparecer en la lista por defecto.
- [ ] Se puede consultar con el filtro "Archivados" y reactivar.
- [ ] La acción pide confirmación y queda auditada.
- [ ] No existe una acción para borrar definitivamente desde la aplicación.

**Prioridad:** alta.

### US-13 — Revisar la auditoría

**Como** Dirección o Administración **quiero** ver quién cambió qué y cuándo **para** responder ante incidentes y revisiones.

**Criterios de aceptación**

- [ ] Solo Dirección y Administración acceden a la auditoría.
- [ ] Se lista actor, acción, registro afectado, fecha y campos cambiados.
- [ ] Se puede filtrar por tipo de registro o acción y buscar por persona o registro.
- [ ] Los cambios muestran valor anterior y nuevo.
- [ ] Las contraseñas nunca aparecen en la auditoría.
- [ ] La auditoría no se puede editar ni eliminar desde la aplicación.

**Prioridad:** alta.

## Historias del incremento 2

### US-14 — Registrar un cuidado durante el turno

**Como** Enfermería, Técnico/a o Cuidador/a **quiero** registrar lo realizado con una persona **para** dejar constancia oportuna y trazable del cuidado.

**Criterios de aceptación**

- [ ] Solo Enfermería, Técnico/a y Cuidador/a pueden registrar; Dirección y Administración reciben HTTP 403.
- [ ] El residente debe estar activo; una ficha archivada bloquea el registro hasta reactivarla.
- [ ] Se registran residente, plan relacionado opcional, fecha y hora, turno, categoría, descripción y observaciones.
- [ ] El plan relacionado debe estar activo y pertenecer al mismo residente.
- [ ] La fecha y hora no puede ser futura (margen de 5 minutos) ni anterior al ingreso.
- [ ] El turno se sugiere según la hora local: mañana 07–15, tarde 15–23, noche 23–07.
- [ ] La descripción exige al menos 10 caracteres; las observaciones admiten hasta 1000.
- [ ] Se puede marcar el registro para revisión de Enfermería.
- [ ] El registro queda asociado a su autor y a la auditoría; no se puede editar ni eliminar después de guardarlo.

**Prioridad:** alta.

### US-15 — Consultar la bandeja de cuidados

**Como** miembro del equipo **quiero** ver los cuidados del día y filtrarlos **para** encontrar rápido lo registrado y lo pendiente.

**Criterios de aceptación**

- [ ] Todos los roles autenticados pueden consultar la bandeja y el detalle.
- [ ] Por defecto se muestran los registros de la fecha local actual.
- [ ] Se puede filtrar por fecha, todas las fechas, turno, categoría, residente o texto.
- [ ] Se puede filtrar solo pendientes de revisión y decidir si se incluyen los corregidos.
- [ ] Los corregidos se ocultan por defecto.
- [ ] Se muestra fecha y hora, turno, residente y habitación, categoría, descripción, autor, estado y marca de revisión.
- [ ] Las acciones visibles respetan el rol y el estado del registro.
- [ ] La bandeja muestra conteos de registros del día, pendientes, planes activos y correcciones del día.
- [ ] La vista se adapta a teléfono, tablet y computador sin desbordamiento horizontal.

**Prioridad:** alta.

### US-16 — Corregir un registro sin borrar el original

**Como** autor del registro o Enfermería **quiero** corregir un dato erróneo **para** mantener la información correcta sin perder el historial.

**Criterios de aceptación**

- [ ] Solo el autor del registro o Enfermería pueden corregirlo; otro rol recibe HTTP 403.
- [ ] Solo se corrige un registro vigente; uno ya corregido redirige a la versión vigente.
- [ ] Una ficha archivada bloquea la corrección.
- [ ] El formulario se precarga con los datos originales y exige un motivo de 10 a 500 caracteres.
- [ ] Al guardar se crea una versión nueva enlazada con `supersedes`; la anterior queda como `CORREGIDO`.
- [ ] El registro original sigue visible en el historial con su autor, fecha y motivo.
- [ ] No se puede corregir dos veces el mismo registro.
- [ ] La corrección queda auditada como acción `CORRECTION`.

**Prioridad:** alta.

### US-17 — Revisar un registro marcado

**Como** Enfermería **quiero** revisar los registros que el equipo marcó **para** validar el cuidado y dejar una respuesta trazable.

**Criterios de aceptación**

- [ ] Solo Enfermería puede revisar; los demás roles reciben HTTP 403.
- [ ] Solo se revisan registros vigentes marcados con `requires_nursing_review=True`.
- [ ] Un registro no marcado, ya revisado o corregido no se puede revisar.
- [ ] Las observaciones de revisión admiten hasta 1000 caracteres.
- [ ] Se guarda quién revisó y cuándo; la revisión queda auditada como `REVIEW`.
- [ ] El detalle muestra la revisión y el registro deja de aparecer como pendiente.
- [ ] Una ficha archivada bloquea la revisión.

**Prioridad:** alta.

### US-18 — Gestionar el plan de cuidados

**Como** Enfermería **quiero** acordar y mantener un plan de cuidados **para** orientar al equipo sin sustituir el criterio profesional.

**Criterios de aceptación**

- [ ] Solo Enfermería puede crear o editar planes; los demás roles solo consultan.
- [ ] El plan registra necesidad o foco, descripción, objetivo, acciones acordadas, responsable, fecha de inicio, próxima revisión y observaciones.
- [ ] La fecha de inicio no puede ser futura y la próxima revisión no puede ser anterior al inicio.
- [ ] El responsable debe ser una cuenta activa de Enfermería, Técnico/a o Cuidador/a.
- [ ] El plan queda asociado al residente y no se puede mover a otro.
- [ ] La creación y cada edición quedan auditadas.
- [ ] El sistema no genera objetivos, acciones ni recomendaciones automáticamente.
- [ ] Una ficha archivada bloquea la creación y edición del plan.

**Prioridad:** alta.

### US-19 — Cerrar o reactivar un plan

**Como** Enfermería **quiero** cerrar un plan cuando deja de aplicar y reactivarlo si vuelve a ser necesario **para** mantener los planes vigentes sin perder el historial.

**Criterios de aceptación**

- [ ] Solo Enfermería puede cerrar o reactivar un plan.
- [ ] El cierre exige un motivo de al menos 10 caracteres y guarda el estado `CERRADO`.
- [ ] El plan cerrado y sus registros asociados se conservan y siguen visibles en el historial.
- [ ] La reactivación vuelve a `ACTIVO`, limpia el motivo de cierre y queda auditada.
- [ ] Una ficha archivada bloquea ambas acciones.
- [ ] No existe una acción para eliminar un plan.

**Prioridad:** alta.

### US-20 — Ver cuidados en la ficha y el panel

**Como** miembro del equipo **quiero** ver el plan y los últimos cuidados dentro de la ficha **para** tener contexto antes de atender a la persona.

**Criterios de aceptación**

- [ ] La ficha tiene una pestaña “Cuidados” con planes activos, planes cerrados y registros recientes.
- [ ] Los registros corregidos se consultan desde el detalle y desde la bandeja al incluir corregidos.
- [ ] Los botones de plan, registro, corrección y revisión solo aparecen para roles autorizados.
- [ ] El panel muestra registros del día, pendientes de revisión y planes activos.
- [ ] El acceso directo a cuidados respeta el inicio de sesión.
- [ ] La navegación por enlace directo muestra la pestaña activa sin ocultar la barra de pestañas bajo el navbar fijo.

**Prioridad:** media.

## Requisitos no funcionales de los incrementos 1 y 2

- **Privacidad:** datos ficticios en desarrollo, pruebas y demos; sin nombres ni RUT reales en repositorios, logs o tickets.
- **Seguridad:** HTTPS en producción, cookies seguras, CSRF, sesiones con vencimiento, contraseñas con algoritmo seguro.
- **Auditoría:** toda escritura sobre residentes, contactos, usuarios, planes y registros de cuidado deja registro; la auditoría es de solo lectura.
- **Trazabilidad clínica:** los registros de cuidado no se editan ni eliminan; las correcciones crean versiones y conservan el original.
- **Revisión:** solo Enfermería revisa registros marcados y la revisión guarda revisor, fecha y observaciones.
- **Accesibilidad:** etiquetas asociadas, foco visible, contraste suficiente y controles de al menos 44 px en móvil.
- **Compatibilidad:** navegadores actuales en teléfono, tablet y computador; diseño adaptable.
- **Conectividad:** las pantallas de consulta y los formularios funcionan sin JavaScript; las pestañas de la ficha usan Bootstrap y HTMX mejora la búsqueda cuando está disponible.
- **Rendimiento:** la lista de residentes y la bandeja de cuidados responden en menos de 2 segundos con el volumen esperado del piloto.
- **Respaldo:** la base de datos de producción debe tener respaldos automáticos y una restauración probada antes del piloto.
- **Criterio profesional:** el sistema no diagnostica, no prioriza clínicamente, no recomienda tratamientos ni genera planes automáticamente.

## Definición de terminado (incrementos 1 y 2)

- [ ] Todas las historias de prioridad alta implementadas.
- [ ] Matriz de permisos cubierta por pruebas automatizadas.
- [ ] Datos ficticios cargables con un comando seguro.
- [ ] README con instalación, ejecución y pruebas.
- [ ] Revisión de la interfaz con al menos una persona de Enfermería y una de Administración.
- [ ] Validación de categorías, turnos, campos, revisión y corrección con el equipo del ELEAM.
- [ ] Revisión legal y de seguridad antes de usar datos reales.
