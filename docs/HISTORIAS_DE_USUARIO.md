# Historias de usuario — Incrementos 1, 2 y 3

Este documento define el alcance funcional de los tres primeros incrementos. Está escrito para validarlo con el equipo del ELEAM antes de ampliarlo. Todas las pruebas y demos usan **datos ficticios**.

**Estado:** los incrementos 1, 2 y 3 están implementados y la suite tiene **115 pruebas automatizadas**. El proyecto está en la etapa de preparación del piloto; las historias marcadas como implementadas describen comportamiento técnico y todavía requieren validación institucional donde se indica.

## Alcance del incremento 1

Incluye:

- Inicio de sesión con cuentas individuales, roles y cierre de sesión.
- Gestión de usuarios por parte de Administración.
- Auditoría de creación, modificación, archivado, desactivación y cambio de contraseña.
- Búsqueda y consulta de residentes.
- Exportación CSV de la nómina de residentes para Dirección, Enfermería y Administración; la descarga queda auditada.
- Ficha administrativa, información clínica relevante (alergias y antecedentes) y contactos.
- Gestión de enfermedades/condiciones y medicamentos, incluida su edición posterior por Enfermería.
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
- Exportaciones de cuidados e incidentes y portal de familias.

## Alcance del incremento 3

Incluye reporte confidencial de incidentes, seguimiento y cierre por roles autorizados, consulta y reportes agregados en un período. Los informes son solo de lectura y no exportan datos. Los roles y campos implementados siguen la propuesta del prototipo y deben validarse con el equipo del ELEAM.

No reemplaza los avisos inmediatos, protocolos institucionales, evaluación profesional ni obligaciones legales de notificación.

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

- [x] El acceso usa correo electrónico y contraseña; no hay usuario compartido.
- [x] Una cuenta desactivada no puede iniciar sesión.
- [x] La sesión expira a las 8 horas o al cerrar el navegador.
- [x] El cierre de sesión se hace con POST y no queda una sesión activa.
- [x] Los errores no revelan si el correo existe o no.
- [x] La pantalla funciona en teléfono, tablet y computador.

**Prioridad:** alta.

### US-02 — Cambiar mi contraseña

**Como** usuario **quiero** cambiar mi contraseña **para** mantener mi cuenta protegida.

**Criterios de aceptación**

- [x] Se solicita la contraseña actual.
- [x] La nueva contraseña cumple la política mínima (10 caracteres, no común, no numérica).
- [x] El cambio queda registrado en auditoría sin guardar la contraseña ni su hash.
- [x] La sesión continúa activa después del cambio.

**Prioridad:** alta.

### US-03 — Gestionar usuarios y roles

**Como** Administración **quiero** crear, editar y desactivar cuentas **para** incorporar y retirar personal de forma controlada.

**Criterios de aceptación**

- [x] Solo Administración puede entrar a la gestión de usuarios.
- [x] Se puede crear una cuenta con correo único, nombre, apellido, rol y contraseña inicial.
- [x] Se puede cambiar el rol y desactivar una cuenta sin eliminarla.
- [x] No se puede desactivar la propia cuenta.
- [x] No se puede dejar el sistema sin una cuenta activa con rol Administración.
- [x] Cada cambio queda auditado con actor y fecha.
- [x] Las contraseñas se almacenan con el algoritmo seguro de Django y nunca se muestran.

**Prioridad:** alta.

### US-04 — Restablecer la contraseña de otra persona

**Como** Administración **quiero** asignar una contraseña temporal **para** ayudar a alguien que no puede entrar.

**Criterios de aceptación**

- [x] Solo Administración puede hacerlo.
- [x] Se pide la nueva contraseña dos veces y se valida la política.
- [x] El cambio se registra en auditoría como acción separada, sin guardar la contraseña.
- [x] Se recomienda a la persona cambiar la contraseña al ingresar.

**Prioridad:** media.

### US-05 — Consultar el panel de inicio

**Como** usuario **quiero** ver un resumen del establecimiento **para** orientarme al comenzar el turno.

**Criterios de aceptación**

- [x] Muestra cantidad de residentes activos y residentes con alergias registradas.
- [x] Muestra los últimos residentes incorporados y alertas de alergias.
- [x] Ofrece accesos directos según el rol.
- [x] No muestra información de auditoría a quien no tiene permiso.
- [x] Se adapta a pantallas pequeñas.

**Prioridad:** media.

### US-06 — Buscar residentes

**Como** miembro del equipo **quiero** buscar por nombre, RUT o habitación **para** encontrar una ficha rápidamente durante el turno.

**Criterios de aceptación**

- [x] La búsqueda es parcial y no distingue mayúsculas ni tildes básicas.
- [x] Se puede filtrar por estado (activo, hospitalizado, egresado) y por archivados.
- [x] Los resultados muestran nombre, RUT, habitación, edad, estado y alerta de alergia.
- [x] Sin JavaScript la búsqueda funciona con el botón "Buscar".
- [x] Con HTMX la lista se actualiza sin recargar la página.
- [x] La lista se pagina y no expone datos a usuarios anónimos.

**Prioridad:** alta.

### US-07 — Ver la ficha de un residente

**Como** miembro del equipo **quiero** ver identificación, contactos y antecedentes relevantes **para** prestar un cuidado seguro y coordinado.

**Criterios de aceptación**

- [x] Se ven datos administrativos, alergias, antecedentes relevantes y contactos.
- [x] Las alergias se destacan visualmente.
- [x] Se ve quién creó y actualizó por última vez la ficha.
- [x] Los botones de edición solo aparecen para roles autorizados.
- [x] La ficha archivada se muestra como archivada y no se puede editar hasta reactivarla.
- [x] Los datos de demostración llevan una marca visible "DEMO".

**Prioridad:** alta.

### US-08 — Crear un residente

**Como** Enfermería o Administración **quiero** registrar el ingreso **para** iniciar la ficha del residente.

**Criterios de aceptación**

- [x] El RUT es obligatorio, válido y único.
- [x] La fecha de nacimiento no puede ser futura y la fecha de ingreso no puede ser anterior al nacimiento.
- [x] Se registran datos mínimos: nombre, apellido, RUT, nacimiento, habitación, ingreso, previsión y estado.
- [x] La información clínica se completa después, solo por Enfermería.
- [x] La creación queda auditada con el usuario y la fecha.
- [x] Un rol no autorizado recibe HTTP 403.

**Prioridad:** alta.

### US-09 — Editar datos administrativos

**Como** Enfermería o Administración **quiero** corregir identificación, habitación, previsión o estado **para** mantener la ficha vigente.

**Criterios de aceptación**

- [x] Solo se editan campos administrativos en este formulario.
- [x] El RUT sigue siendo único.
- [x] Los cambios quedan auditados con valor anterior y nuevo.
- [x] No se puede editar una ficha archivada sin reactivarla.
- [x] Técnico/a, Cuidador/a y Dirección reciben HTTP 403 si intentan editar.

**Prioridad:** alta.

### US-10 — Editar información clínica relevante

**Como** Enfermería **quiero** actualizar alergias y antecedentes **para** que el resto del equipo cuide con información correcta.

**Criterios de aceptación**

- [x] Solo Enfermería puede editar alergias, antecedentes y observaciones clínicas.
- [x] El formulario advierte que no se deben registrar diagnósticos innecesarios ni datos de terceros.
- [x] Cada cambio queda auditado con valor anterior y nuevo.
- [x] Los demás roles ven la información en modo lectura.

**Prioridad:** alta.

### US-11 — Gestionar contactos

**Como** Enfermería o Administración **quiero** mantener los contactos del residente **para** comunicarnos con quien corresponda.

**Criterios de aceptación**

- [x] Se puede crear, editar y eliminar un contacto con nombre, parentesco, teléfono, correo y notas.
- [x] Solo puede haber un contacto principal por residente; al marcarlo se desmarca el anterior.
- [x] Se muestra quién es el contacto principal en la ficha.
- [x] La eliminación pide confirmación y queda auditada con los datos anteriores.
- [x] Técnico/a, Cuidador/a y Dirección no pueden modificar contactos.

**Prioridad:** alta.

### US-12 — Archivar y reactivar residentes

**Como** Enfermería o Administración **quiero** archivar una ficha cuando la persona egresa **para** conservar el historial sin mezclarla con los residentes activos.

**Criterios de aceptación**

- [x] Archivar no elimina la ficha ni sus contactos.
- [x] La ficha archivada deja de aparecer en la lista por defecto.
- [x] Se puede consultar con el filtro "Archivados" y reactivar.
- [x] La acción pide confirmación y queda auditada.
- [x] No existe una acción para borrar definitivamente desde la aplicación.

**Prioridad:** alta.

### US-13 — Revisar la auditoría

**Como** Dirección o Administración **quiero** ver quién cambió qué y cuándo **para** responder ante incidentes y revisiones.

**Criterios de aceptación**

- [x] Solo Dirección y Administración acceden a la auditoría.
- [x] Se lista actor, acción, registro afectado, fecha y campos cambiados.
- [x] Se puede filtrar por tipo de registro o acción y buscar por persona o registro.
- [x] Los cambios muestran valor anterior y nuevo.
- [x] Las contraseñas nunca aparecen en la auditoría.
- [x] La auditoría no se puede editar ni eliminar desde la aplicación.

**Prioridad:** alta.

## Historias del incremento 2

### US-14 — Registrar un cuidado durante el turno

**Como** Enfermería, Técnico/a o Cuidador/a **quiero** registrar lo realizado con una persona **para** dejar constancia oportuna y trazable del cuidado.

**Criterios de aceptación**

- [x] Solo Enfermería, Técnico/a y Cuidador/a pueden registrar; Dirección y Administración reciben HTTP 403.
- [x] El residente debe estar activo; una ficha archivada bloquea el registro hasta reactivarla.
- [x] Se registran residente, plan relacionado opcional, fecha y hora, turno, categoría, descripción y observaciones.
- [x] El plan relacionado debe estar activo y pertenecer al mismo residente.
- [x] La fecha y hora no puede ser futura (margen de 5 minutos) ni anterior al ingreso.
- [x] El turno se sugiere según la hora local: mañana 07–15, tarde 15–23, noche 23–07.
- [x] La descripción exige al menos 10 caracteres; las observaciones admiten hasta 1000.
- [x] Se puede marcar el registro para revisión de Enfermería.
- [x] El registro queda asociado a su autor y a la auditoría; no se puede editar ni eliminar después de guardarlo.

**Prioridad:** alta.

### US-15 — Consultar la bandeja de cuidados

**Como** miembro del equipo **quiero** ver los cuidados del día y filtrarlos **para** encontrar rápido lo registrado y lo pendiente.

**Criterios de aceptación**

- [x] Todos los roles autenticados pueden consultar la bandeja y el detalle.
- [x] Por defecto se muestran los registros de la fecha local actual.
- [x] Se puede filtrar por fecha, todas las fechas, turno, categoría, residente o texto.
- [x] Se puede filtrar solo pendientes de revisión y decidir si se incluyen los corregidos.
- [x] Los corregidos se ocultan por defecto.
- [x] Se muestra fecha y hora, turno, residente y habitación, categoría, descripción, autor, estado y marca de revisión.
- [x] Las acciones visibles respetan el rol y el estado del registro.
- [x] La bandeja muestra conteos de registros del día, pendientes, planes activos y correcciones del día.
- [x] La vista se adapta a teléfono, tablet y computador sin desbordamiento horizontal.

**Prioridad:** alta.

### US-16 — Corregir un registro sin borrar el original

**Como** autor del registro o Enfermería **quiero** corregir un dato erróneo **para** mantener la información correcta sin perder el historial.

**Criterios de aceptación**

- [x] Solo el autor del registro o Enfermería pueden corregirlo; otro rol recibe HTTP 403.
- [x] Solo se corrige un registro vigente; uno ya corregido redirige a la versión vigente.
- [x] Una ficha archivada bloquea la corrección.
- [x] El formulario se precarga con los datos originales y exige un motivo de 10 a 500 caracteres.
- [x] Al guardar se crea una versión nueva enlazada con `supersedes`; la anterior queda como `CORREGIDO`.
- [x] El registro original sigue visible en el historial con su autor, fecha y motivo.
- [x] No se puede corregir dos veces el mismo registro.
- [x] La corrección queda auditada como acción `CORRECTION`.

**Prioridad:** alta.

### US-17 — Revisar un registro marcado

**Como** Enfermería **quiero** revisar los registros que el equipo marcó **para** validar el cuidado y dejar una respuesta trazable.

**Criterios de aceptación**

- [x] Solo Enfermería puede revisar; los demás roles reciben HTTP 403.
- [x] Solo se revisan registros vigentes marcados con `requires_nursing_review=True`.
- [x] Un registro no marcado, ya revisado o corregido no se puede revisar.
- [x] Las observaciones de revisión admiten hasta 1000 caracteres.
- [x] Se guarda quién revisó y cuándo; la revisión queda auditada como `REVIEW`.
- [x] El detalle muestra la revisión y el registro deja de aparecer como pendiente.
- [x] Una ficha archivada bloquea la revisión.

**Prioridad:** alta.

### US-18 — Gestionar el plan de cuidados

**Como** Enfermería **quiero** acordar y mantener un plan de cuidados **para** orientar al equipo sin sustituir el criterio profesional.

**Criterios de aceptación**

- [x] Solo Enfermería puede crear o editar planes; los demás roles solo consultan.
- [x] El plan registra necesidad o foco, descripción, objetivo, acciones acordadas, responsable, fecha de inicio, próxima revisión y observaciones.
- [x] La fecha de inicio no puede ser futura y la próxima revisión no puede ser anterior al inicio.
- [x] El responsable debe ser una cuenta activa de Enfermería, Técnico/a o Cuidador/a.
- [x] El plan queda asociado al residente y no se puede mover a otro.
- [x] La creación y cada edición quedan auditadas.
- [x] El sistema no genera objetivos, acciones ni recomendaciones automáticamente.
- [x] Una ficha archivada bloquea la creación y edición del plan.

**Prioridad:** alta.

### US-19 — Cerrar o reactivar un plan

**Como** Enfermería **quiero** cerrar un plan cuando deja de aplicar y reactivarlo si vuelve a ser necesario **para** mantener los planes vigentes sin perder el historial.

**Criterios de aceptación**

- [x] Solo Enfermería puede cerrar o reactivar un plan.
- [x] El cierre exige un motivo de al menos 10 caracteres y guarda el estado `CERRADO`.
- [x] El plan cerrado y sus registros asociados se conservan y siguen visibles en el historial.
- [x] La reactivación vuelve a `ACTIVO`, limpia el motivo de cierre y queda auditada.
- [x] Una ficha archivada bloquea ambas acciones.
- [x] No existe una acción para eliminar un plan.

**Prioridad:** alta.

### US-20 — Ver cuidados en la ficha y el panel

**Como** miembro del equipo **quiero** ver el plan y los últimos cuidados dentro de la ficha **para** tener contexto antes de atender a la persona.

**Criterios de aceptación**

- [x] La ficha tiene una pestaña “Cuidados” con planes activos, planes cerrados y registros recientes.
- [x] Los registros corregidos se consultan desde el detalle y desde la bandeja al incluir corregidos.
- [x] Los botones de plan, registro, corrección y revisión solo aparecen para roles autorizados.
- [x] El panel muestra registros del día, pendientes de revisión y planes activos.
- [x] El acceso directo a cuidados respeta el inicio de sesión.
- [x] La navegación por enlace directo muestra la pestaña activa sin ocultar la barra de pestañas bajo el navbar fijo.

**Prioridad:** media.

### US-21 — Reportar un incidente

**Como** Enfermería, Técnico/a o Cuidador/a **quiero** registrar un incidente y las acciones inmediatas **para** dejar un antecedente trazable y apoyar el seguimiento.

**Criterios de aceptación**

- [x] Se registra residente, fecha/hora, tipo, lugar, gravedad percibida, hechos, acciones tomadas, personas presentes y notificaciones pertinentes.
- [x] Solo se seleccionan residentes con ficha activa y la fecha no puede ser futura ni anterior al ingreso.
- [x] La descripción y las acciones exigen texto suficiente y objetivo.
- [x] El reporte queda asociado al autor y a auditoría.
- [x] Dirección, Enfermería, Técnico/a y Cuidador/a pueden consultar; Administración no accede al módulo.
- [x] El aviso y los protocolos institucionales no se sustituyen por guardar el formulario.

**Prioridad:** alta.

### US-22 — Dar seguimiento y cerrar un incidente

**Como** Enfermería o Dirección **quiero** registrar el seguimiento y cerrar un incidente **para** conservar una respuesta trazable sin sobrescribir el reporte original.

**Criterios de aceptación**

- [x] Solo Enfermería o Dirección pueden cerrar.
- [x] El cierre requiere un motivo/seguimiento y guarda actor y fecha.
- [x] El reporte original se conserva y el cierre queda en auditoría.
- [x] Un incidente cerrado no se vuelve a cerrar ni se modifica desde la aplicación.

**Prioridad:** alta.

### US-23 — Consultar informes básicos de incidentes

**Como** Enfermería o Dirección **quiero** ver conteos por período, tipo, gravedad percibida y estado **para** apoyar la revisión operativa.

**Criterios de aceptación**

- [x] Se puede seleccionar un período válido.
- [x] Se muestran totales, abiertos, cerrados y distribuciones por tipo y gravedad percibida.
- [x] Solo Enfermería y Dirección acceden a los informes.
- [x] El informe es agregado, no exporta datos y no realiza conclusiones clínicas.

**Prioridad:** media.

## Funcionalidad adicional implementada

**Como** Dirección, Enfermería o Administración **quiero** descargar la nómina filtrada de residentes **para** realizar tareas autorizadas.

### US-24 — Exportar la nómina de residentes

**Criterios de aceptación implementados en el código**

- [x] Solo Dirección, Enfermería y Administración pueden acceder a la exportación CSV.
- [x] Se aplican los filtros de búsqueda, estado y fichas archivadas de la lista de residentes.
- [x] La descarga registra en auditoría los filtros utilizados y el total de fichas exportadas.
- [x] La nómina incluye RUT, nombres y apellidos, nombre preferido, nacimiento, edad, sexo, habitación, previsión, estado, fecha de ingreso y nombre, parentesco y teléfono del contacto principal; el archivo es sensible.
- [x] No existe exportación de registros de cuidados ni de reportes de incidentes.

**Cobertura automatizada:** permisos por rol, filtros de búsqueda/estado/archivados y evento de auditoría de la descarga (7 pruebas).

**Pendiente de validación institucional:** confirmar que los roles, campos exportados y manejo de archivos descargados son adecuados antes de usar datos reales.

### US-25 — Mantener enfermedades y condiciones

**Como** Enfermería **quiero** registrar, actualizar o retirar una enfermedad/condición de la ficha **para** mantener vigente la información clínica del residente.

**Criterios de aceptación**

- [x] Se registra el nombre, fecha de diagnóstico opcional, estado y observaciones.
- [x] Enfermería puede editar la información después de guardarla y eliminarla con confirmación.
- [x] Cada creación, edición y eliminación queda auditada.
- [x] El resto de los roles autorizados puede consultar la información, pero no modificarla.
- [x] Una ficha archivada bloquea estos cambios.

**Prioridad:** alta.

### US-26 — Mantener medicamentos

**Como** Enfermería **quiero** registrar y actualizar los medicamentos de un residente **para** que el equipo autorizado consulte las indicaciones vigentes.

**Criterios de aceptación**

- [x] Se registra nombre, dosis, frecuencia u horario, vía, estado, profesional que indica, fechas opcionales, instrucciones y observaciones.
- [x] Enfermería puede editar los datos después de guardarlos y eliminar el registro con confirmación.
- [x] La fecha de término no puede ser anterior a la fecha de inicio.
- [x] Cada creación, edición y eliminación queda auditada.
- [x] El resto de los roles autorizados puede consultar la información, pero no modificarla; una ficha archivada bloquea cambios.

**Prioridad:** alta.

## Requisitos no funcionales de los incrementos 1, 2 y 3

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

## Definición de terminado (incrementos 1, 2 y 3)

- [x] Historias US-01 a US-23 implementadas y cubiertas técnicamente por pruebas.
- [x] Exportación CSV de residentes implementada según US-24 y cubierta por pruebas de permisos, filtros y auditoría.
- [x] Gestión de enfermedades y medicamentos implementada según US-25 y US-26, con edición posterior y auditoría.
- [x] Matriz de permisos cubierta por pruebas automatizadas en la suite pytest.
- [x] Datos ficticios cargables con un comando seguro (`seed_demo`).
- [x] README con instalación, lanzador de Windows (`iniciar.bat`), ejecución y pruebas.
- [ ] Revisión de la interfaz con al menos una persona de Enfermería y una de Administración.
- [ ] Validación de categorías, turnos, campos, revisión y corrección con el equipo del ELEAM.
- [ ] Revisión legal y de seguridad antes de usar datos reales.
- [ ] Validar los campos, roles y criterios de seguimiento de incidentes con el ELEAM.
- [x] Añadir o confirmar pruebas automatizadas de permisos, filtros y auditoría de la exportación CSV.
