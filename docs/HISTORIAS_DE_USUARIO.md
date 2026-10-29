# Historias de usuario — Incremento 1

Este documento define el alcance funcional del primer incremento. Está escrito para validarlo con el equipo del ELEAM antes de ampliarlo. Todas las pruebas y demos usan **datos ficticios**.

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

- Registros diarios de cuidados y plan de cuidados (incremento 2).
- Incidentes e informes (incremento 3).
- Portal de familias, facturación, inventario, integraciones o aplicación móvil nativa.
- Alertas automáticas, recomendaciones clínicas o cualquier función que decida tratamientos.
- Migración de registros históricos.

## Actores

- **Dirección:** supervisa, consulta y revisa auditoría.
- **Enfermería:** mantiene la ficha clínica y administrativa.
- **Técnico/a y Cuidador/a:** consultan la ficha para cuidar con seguridad.
- **Administración:** gestiona datos administrativos, contactos y usuarios.
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

## Requisitos no funcionales del incremento

- **Privacidad:** datos ficticios en desarrollo, pruebas y demos; sin nombres ni RUT reales en repositorios, logs o tickets.
- **Seguridad:** HTTPS en producción, cookies seguras, CSRF, sesiones con vencimiento, contraseñas con algoritmo seguro.
- **Auditoría:** toda escritura sobre residentes, contactos y usuarios deja registro; la auditoría es de solo lectura.
- **Accesibilidad:** etiquetas asociadas, foco visible, contraste suficiente y controles de al menos 44 px en móvil.
- **Compatibilidad:** navegadores actuales en teléfono, tablet y computador; diseño adaptable.
- **Conectividad:** las pantallas principales funcionan sin JavaScript; HTMX mejora la búsqueda cuando está disponible.
- **Rendimiento:** la lista de residentes responde en menos de 2 segundos con hasta 300 residentes en el piloto.
- **Respaldo:** la base de datos de producción debe tener respaldos automáticos y una restauración probada antes del piloto.

## Definición de terminado (incremento 1)

- [ ] Todas las historias de prioridad alta implementadas.
- [ ] Matriz de permisos cubierta por pruebas automatizadas.
- [ ] Datos ficticios cargables con un comando seguro.
- [ ] README con instalación, ejecución y pruebas.
- [ ] Revisión de la interfaz con al menos una persona de Enfermería y una de Administración.
- [ ] Revisión legal y de seguridad antes de usar datos reales.
