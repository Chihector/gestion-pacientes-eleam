# Tecnologías recomendadas

## Propuesta inicial

Para un equipo pequeño o un primer producto, elegiría una aplicación web adaptable a teléfonos, tablets y computadores. Esta combinación prioriza simplicidad de operación y reduce la cantidad de piezas que hay que mantener.

| Capa | Recomendación | Motivo |
|---|---|---|
| Lenguaje y servidor | Python + Django | Incluye herramientas maduras para formularios, usuarios, permisos y administración. |
| Interfaz | Plantillas Django + HTMX + Bootstrap | Permite una interfaz adaptable sin mantener una aplicación frontend separada. |
| Base de datos | PostgreSQL | Adecuada para datos relacionales, consultas e integridad referencial. |
| Pruebas | Pruebas de Django; pytest-django si el proyecto lo requiere | Verifica reglas, permisos y flujos importantes. |
| Control de versiones | Git + repositorio privado | Facilita revisar cambios y recuperar versiones del código. |
| Desarrollo local | Docker Compose, opcional | Ayuda a que el equipo use versiones consistentes de la aplicación y la base de datos. |
| Producción | Servicio administrado compatible con Django y PostgreSQL | Reduce tareas de operación; elegirlo solo tras revisar contrato, ubicación, acceso y respaldos. |

No comenzaría con microservicios, una app móvil nativa ni una arquitectura frontend/backend separada: añaden complejidad antes de que estén validados los flujos.

## Seguridad y privacidad desde el diseño

- Usar HTTPS, contraseñas almacenadas con algoritmos seguros y sesiones con vencimiento.
- Usar cuentas individuales; no compartir usuarios entre turnos.
- Aplicar permisos por rol y comprobarlos en el servidor, no solo ocultar botones.
- Registrar quién creó o modificó datos relevantes, cuándo y qué cambió; restringir el acceso a la auditoría.
- No incluir nombres, diagnósticos ni otros datos de residentes en logs técnicos, analítica, tickets o repositorios.
- Cifrar respaldos, limitar quién puede descargarlos y probar restauraciones periódicamente.
- Configurar copias de seguridad automáticas y documentar cuánto se conserva cada copia.
- Mantener secretos y claves fuera del código; usar el gestor de secretos del proveedor.
- Evitar computadores compartidos sin bloqueo de pantalla y establecer un procedimiento ante pérdida de dispositivos.
- Evaluar proveedores, contratos, ubicación de almacenamiento y acceso de soporte antes de alojar información real.

La aplicación no debería usar inteligencia artificial para diagnosticar, recomendar tratamientos o decidir prioridades clínicas. No enviar información de residentes a servicios externos de IA.

## Datos de salud y contexto chileno

Antes del piloto, pedir una revisión de las obligaciones aplicables al ELEAM y a sus actividades, incluyendo protección de datos personales, información de salud, derechos de las personas y contratos con proveedores. Revisar la normativa chilena vigente —incluidas las leyes 19.628, 20.584 y 21.719, según corresponda— con asesoría jurídica; no asumir que una configuración técnica por sí sola garantiza cumplimiento.

Definir con el ELEAM políticas documentadas para finalidad y acceso, información a residentes o representantes, corrección de datos, conservación, eliminación, incidentes y solicitudes de acceso. Recopilar solo lo necesario y no migrar registros antiguos sin una justificación y un plan de calidad.

## Entorno y despliegue

**Desarrollo:** computador local, base de datos de desarrollo y datos ficticios. El repositorio debe ser privado y no contener datos operacionales.

**Pruebas:** entorno separado de producción, con datos ficticios y credenciales distintas. Automatizar pruebas y revisión de cambios antes de desplegar.

**Producción:** proveedor administrado que cumpla los requisitos definidos por el ELEAM. Confirmar ubicación y transferencias de datos, controles de acceso, disponibilidad, respaldos, restauración, soporte, contrato y proceso de salida del proveedor. No decidir el proveedor solo por precio.

## Cuándo considerar otras opciones

- **Django REST Framework + frontend separado:** si más adelante se necesita una app móvil o integraciones que justifiquen mantener dos aplicaciones.
- **Aplicación móvil nativa:** solo si se valida una necesidad que la web adaptable no resuelve, como captura sin conexión confiable.
- **Otra plataforma o proveedor:** si el ELEAM ya tiene soporte técnico, contratos o infraestructura aprobada que favorezcan esa opción.

La elección final debe considerar quién mantendrá el sistema después del piloto. Un stack conocido por el equipo suele ser mejor que uno técnicamente más novedoso pero sin soporte.
