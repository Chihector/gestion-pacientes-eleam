@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"

set "PY=%USERPROFILE%\.venvs\eleam\Scripts\python.exe"

if not exist "%PY%" (
    echo.
    echo No se encontro el entorno virtual de Python en:
    echo   %PY%
    echo.
    echo Ejecuta primero instalar.bat. Consulta docs\INSTALACION_LOCAL.md.
    pause
    exit /b 1
)

set "NEW_DB=0"
if not exist "db.sqlite3" if not exist ".initialized" set "NEW_DB=1"

echo Actualizando la base de datos...
"%PY%" manage.py migrate || goto :error

if "%NEW_DB%"=="1" (
    echo Cargando datos ficticios de demostracion...
    "%PY%" manage.py seed_demo || goto :error
    type nul > .initialized
)

echo.
echo Iniciando ELEAM en http://127.0.0.1:8000/cuenta/login/
echo Para detener el servidor presiona Ctrl+C o cierra esta ventana.
echo.

if not "%ELEAM_NO_BROWSER%"=="1" start "" powershell -NoProfile -WindowStyle Hidden -Command "Start-Sleep -Seconds 3; Start-Process 'http://127.0.0.1:8000/cuenta/login/'"
"%PY%" manage.py runserver 127.0.0.1:8000
goto :end

:error
echo.
echo No se pudo preparar la base de datos. Revisa el mensaje anterior.
pause

:end
