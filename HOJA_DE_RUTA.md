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
3. Registros diarios, plan de cuidados, correcciones y revisión de Enfermería. **Implementado, pendiente de validación con el equipo.**
4. Incidentes, consulta e informes básicos. **Pendiente.**
5. Pruebas automatizadas, respaldos y documentación operativa. **En curso: 67 pruebas y documentación de los incrementos 1 y 2.**

Construir primero con datos ficticios. Revisar cada entrega con el personal del ELEAM. Registrar los cambios de forma que una corrección no borre silenciosamente el dato original.

## Etapa 5: pruebas y preparación del piloto

- Probar permisos: cada rol ve y modifica solo lo autorizado.
- Probar casos normales y errores: campos incompletos, duplicados, correcciones y usuarios desactivados.
- Probar que el historial de cambios es consultable por personal autorizado.
- Ensayar una restauración desde un respaldo.
- Preparar un procedimiento manual temporal si se cae el sistema o internet.
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

- [ ] Número de residentes, funcionarios y turnos que debe soportar el piloto.
- [ ] Dispositivos disponibles y calidad de internet en las áreas de atención.
- [ ] Formularios y registros que se usarán en el MVP.
- [ ] Roles definitivos y permisos asociados.
- [ ] Proveedor de alojamiento y ubicación de los datos.
- [ ] Requisitos de conservación, acceso, corrección y eliminación de datos.
- [ ] Responsable de soporte y respuesta ante incidentes.
