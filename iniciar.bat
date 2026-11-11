@echo off
setlocal
cd /d "%~dp0"
title Alma Buffet (desarrollo)

set "PY_VENV=venv\Scripts\python.exe"

if not exist "%PY_VENV%" goto :crear_venv
"%PY_VENV%" -c "import sys" >nul 2>&1
if not errorlevel 1 goto :dependencias
echo El entorno virtual no corresponde a esta computadora. Se va a crear de nuevo...
rmdir /s /q venv

:crear_venv
call :buscar_python
if errorlevel 1 goto :sin_python
echo Creando el entorno virtual con %PYTHON%...
%PYTHON% -m venv venv
if errorlevel 1 goto :error

:dependencias
fc /b requirements.txt venv\requisitos_instalados.txt >nul 2>&1
if not errorlevel 1 goto :base_datos
echo Instalando dependencias, puede tardar unos minutos...
"%PY_VENV%" -m pip install --disable-pip-version-check -q -r requirements.txt
if errorlevel 1 goto :error
copy /y requirements.txt venv\requisitos_instalados.txt >nul

:base_datos
"%PY_VENV%" -m flask --app run migrar --crear-base
if errorlevel 1 goto :error

"%PY_VENV%" -m flask --app run inicializar-admin --si-falta
if errorlevel 1 goto :error

echo Iniciando Alma Buffet en http://127.0.0.1:5000 ...
start "" "http://127.0.0.1:5000"
"%PY_VENV%" run.py
if errorlevel 1 goto :error
exit /b 0

:buscar_python
for %%P in ("py -3.11" "py -3" "python") do (
    %%~P -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>&1
    if not errorlevel 1 (
        set "PYTHON=%%~P"
        exit /b 0
    )
)
exit /b 1

:sin_python
echo.
echo No se encontro Python 3.10 o superior.
echo Instalelo desde https://www.python.org/downloads/ marcando "Add Python to PATH".
pause
exit /b 1

:error
echo.
echo Ocurrio un error. Revise los mensajes de arriba.
pause
exit /b 1
