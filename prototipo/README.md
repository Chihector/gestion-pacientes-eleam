# Prototipo navegable

Este prototipo sirve para **conversar con el equipo del ELEAM antes de programar**. No tiene backend, no guarda información y no debe usarse con datos reales.

## Cómo abrirlo

Abre `login.html` directamente en el navegador, o levanta un servidor local desde esta carpeta:

```bash
python -m http.server 8080
```

Luego visita <http://localhost:8080/login.html>.

También puedes abrir los archivos `.html` con doble clic; los estilos y scripts están incluidos localmente, así que funciona sin internet.

## Selector de rol

En la barra superior hay un selector **"Ver como"**. Cambia entre:

- Enfermería
- Administración
- Técnico/a
- Cuidador/a
- Dirección

El prototipo oculta botones y secciones según el rol para mostrar la intención de la matriz de permisos. **Esto es solo una simulación visual:** en la aplicación real el servidor valida cada permiso y devuelve HTTP 403 cuando corresponde.

## Páginas

| Archivo | Flujo que permite probar |
|---|---|
| `login.html` | Acceso con cuenta individual y advertencia de equipo compartido. |
| `panel.html` | Resumen del turno, alertas de cuidado y accesos rápidos. |
| `residentes.html` | Búsqueda por nombre/RUT/habitación, filtros y ficha archivada. |
| `ficha.html` | Datos administrativos, alergias, antecedentes, contactos y actividad. |
| `registro-diario.html` | Registro de cuidados del incremento 2 (propuesta). |
| `incidente.html` | Reporte de incidentes del incremento 3 (propuesta). |
| `auditoria.html` | Historial de cambios y bloqueo para roles no autorizados. |
| `usuarios.html` | Gestión de cuentas y roles, solo para Administración. |

## Qué observar con el personal

1. ¿Encuentran a un residente en menos de 10 segundos?
2. ¿La alergia se ve antes de cualquier otra acción?
3. ¿El formulario de cuidado se puede completar de pie, en un teléfono, durante el turno?
4. ¿Los campos del reporte de incidentes coinciden con lo que realmente registran?
5. ¿Los roles y permisos reflejan cómo trabaja el equipo?
6. ¿Qué información falta, sobra o confunde?

Anota las respuestas y ajusta los formularios antes de implementar. No se debe iniciar un piloto con datos reales hasta revisar seguridad, privacidad, capacitación y continuidad operacional.

## Limitaciones

- No hay autenticación real: los datos están escritos en el HTML.
- Los formularios simulan el guardado con un aviso; no persisten nada.
- Los filtros de residentes funcionan en el navegador.
- La auditoría y la gestión de usuarios son demostraciones visuales.
- Los nombres, RUT, teléfonos y antecedentes son ficticios.

## Archivos

- `assets/estilos.css`: diseño adaptable y componentes visuales.
- `assets/demo.js`: selector de rol, filtros y simulación de acciones.
- `assets/vendor/`: Bootstrap 5.3.3 y Bootstrap Icons 1.11.3 incluidos localmente.
