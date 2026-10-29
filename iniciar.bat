@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"

set "PY=C:\Users\hecto\.venvs\eleam\Scripts\python.exe"

if not exist "%PY%" (
    echo.
    echo No se encontro el entorno virtual de Python en:
    echo   %PY%
    echo.
    echo Revisa la seccion "Instalacion local" del README.md.
    pause
    exit /b 1
)

if not exist "db.sqlite3" (
    echo Preparando la base de datos de demostracion...
    "%PY%" manage.py migrate || goto :error
    "%PY%" manage.py seed_demo || goto :error
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
