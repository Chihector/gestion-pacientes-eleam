# Instalación local en Windows

Esta modalidad instala una copia independiente para pruebas, demostraciones o uso local en **un solo PC**. Cada PC tendrá su propia base `db.sqlite3`; los datos no se comparten ni sincronizan entre equipos. Para que varias personas usen la misma información, revisa [Publicación web](PUBLICACION_WEB.md).

## Requisitos

- Windows 10 u 11.
- Python 3.11 instalado desde [python.org](https://www.python.org/downloads/windows/) con el lanzador `py`.
- Conexión a internet durante la primera instalación, para descargar Django y sus dependencias.

## Instalar y arrancar

1. Descarga el repositorio como ZIP o clónalo con Git.
2. Descomprime o ubica el proyecto en una carpeta local, por ejemplo `C:\ELEAM`. Evita OneDrive, carpetas de red y unidades sincronizadas para la base de datos.
3. Haz doble clic en `instalar.bat`. Crea el entorno virtual en `%USERPROFILE%\.venvs\eleam`, instala dependencias, aplica migraciones y carga datos ficticios si todavía no existe la base local.
4. Haz doble clic en `iniciar.bat` y abre `http://127.0.0.1:8000/cuenta/login/`.
5. Para detener el servidor, vuelve a la ventana negra y presiona `Ctrl+C`.

Las cuentas y contraseña de demostración están en la sección “Cuentas de demostración” del [README principal](../README.md). Son solo para datos ficticios. El comando de carga demo restaura las contraseñas conocidas; no lo uses con información real.

## Actualizar la copia

1. Cierra el servidor con `Ctrl+C`.
2. Haz una copia protegida de `db.sqlite3` antes de actualizar.
3. Actualiza los archivos del proyecto sin reemplazar tu base local.
4. Ejecuta `instalar.bat` para instalar dependencias nuevas y aplicar migraciones; luego abre `iniciar.bat`.

No borres `db.sqlite3` para actualizar. Borrarla elimina los datos locales de esa instalación.

## Límites de esta modalidad

- La aplicación solo escucha en `127.0.0.1`: se accede desde el mismo PC.
- Cada copia mantiene sus propios usuarios y datos.
- No es un instalador ejecutable independiente: el PC requiere Python 3.11.
- El servidor incluido es el servidor de desarrollo de Django; esta instalación es para desarrollo/demostración y no debe exponerse a internet ni usarse como servidor productivo.
- Usa exclusivamente datos ficticios hasta completar las validaciones legales, de seguridad y operativas descritas en la hoja de ruta.
