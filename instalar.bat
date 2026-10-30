@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"

set "VENV=%USERPROFILE%\.venvs\eleam"
set "PY=%VENV%\Scripts\python.exe"

where py >nul 2>nul
if errorlevel 1 (
    echo.
    echo No se encontro el lanzador de Python ^(py^).
    echo Instala Python 3.11 desde https://www.python.org/downloads/windows/
    echo y vuelve a ejecutar este archivo.
    pause
    exit /b 1
)

if not exist "%PY%" (
    echo Creando entorno Python en "%VENV%"...
    py -3.11 -m venv "%VENV%" || goto :error
)

echo Instalando dependencias...
"%PY%" -m pip install -r requirements.txt || goto :error

set "NEW_DB=0"
if not exist "db.sqlite3" set "NEW_DB=1"

echo Preparando la base de datos...
"%PY%" manage.py migrate || goto :error

if "%NEW_DB%"=="1" (
    echo Cargando datos ficticios de demostracion...
    "%PY%" manage.py seed_demo || goto :error
)

echo.
echo Instalacion terminada. Ejecuta iniciar.bat para abrir la aplicacion.
pause
exit /b 0

:error
echo.
echo No se pudo completar la instalacion. Revisa el error anterior.
pause
exit /b 1
