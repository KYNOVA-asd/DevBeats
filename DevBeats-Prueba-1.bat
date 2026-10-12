@echo off
setlocal EnableExtensions
chcp 65001 >nul
cd /d "%~dp0"
title DevBeats - Prueba 1

set "VENV_PY=%~dp0.venv\Scripts\python.exe"

if not exist "%VENV_PY%" (
    echo [DevBeats] Preparando el entorno por primera vez...
    where py >nul 2>nul
    if not errorlevel 1 (
        py -3.12 -m venv .venv
    ) else (
        where python >nul 2>nul
        if errorlevel 1 goto :python_missing
        python -m venv .venv
    )
    if errorlevel 1 goto :setup_failed
)

"%VENV_PY%" -c "import devbeats" >nul 2>nul
if errorlevel 1 (
    echo [DevBeats] Instalando dependencias...
    "%VENV_PY%" -m pip install -r requirements.txt
    if errorlevel 1 goto :setup_failed
    "%VENV_PY%" -m pip install -e .
    if errorlevel 1 goto :setup_failed
)

:menu
cls
echo ========================================================
echo                    DEVBEATS - PRUEBA 1
echo ========================================================
echo.
echo   1. Crear una cancion nueva
echo   2. Ver estado del proyecto activo
echo   3. Construir MIDI y proyecto LMMS
echo   4. Mostrar ayuda de DevBeats
echo   5. Abrir carpeta del proyecto
echo   6. Probar conexion con Gemini
echo   7. Buscar musica con Google IA
echo   8. Crear cancion con Gemini + Google Search
echo   9. Importar letra y acordes para LMMS
echo   0. Salir
echo.
set "OPTION="
set /p "OPTION=Selecciona una opcion: "

if "%OPTION%"=="1" goto :new_song
if "%OPTION%"=="2" goto :status
if "%OPTION%"=="3" goto :build
if "%OPTION%"=="4" goto :help
if "%OPTION%"=="5" goto :open_folder
if "%OPTION%"=="6" goto :ai_test
if "%OPTION%"=="7" goto :google_search
if "%OPTION%"=="8" goto :ai_plan
if "%OPTION%"=="9" goto :import_chords
if "%OPTION%"=="0" goto :end
echo.
echo Opcion no valida.
pause
goto :menu

:new_song
echo.
set "SONG_NAME="
set /p "SONG_NAME=Nombre de la cancion: "
if not defined SONG_NAME goto :menu
"%VENV_PY%" -m devbeats.main new "%SONG_NAME%"
echo.
pause
goto :menu

:status
echo.
"%VENV_PY%" -m devbeats.main status
echo.
pause
goto :menu

:build
echo.
"%VENV_PY%" -m devbeats.main build
echo.
if not errorlevel 1 echo Archivos generados correctamente.
pause
goto :menu

:help
echo.
"%VENV_PY%" -m devbeats.main --help
echo.
pause
goto :menu

:open_folder
start "" explorer.exe "%~dp0"
goto :menu

:ai_test
echo.
"%VENV_PY%" -m devbeats.main ai-test
echo.
pause
goto :menu

:google_search
echo.
set "SEARCH_QUERY="
set /p "SEARCH_QUERY=Que quieres investigar: "
if not defined SEARCH_QUERY goto :menu
"%VENV_PY%" -m devbeats.main search "%SEARCH_QUERY%"
echo.
pause
goto :menu

:ai_plan
echo.
set "SONG_REQUEST="
set /p "SONG_REQUEST=Describe la cancion que quieres: "
if not defined SONG_REQUEST goto :menu
"%VENV_PY%" -m devbeats.main ai-plan "%SONG_REQUEST%"
echo.
pause
goto :menu

:import_chords
echo.
set "CHORD_FILE="
set /p "CHORD_FILE=Ruta de canciones o del archivo TXT: "
if not defined CHORD_FILE goto :menu
set "CHORD_TITLE="
set /p "CHORD_TITLE=Titulo de la cancion: "
if not defined CHORD_TITLE set "CHORD_TITLE=Cancion importada"
"%VENV_PY%" -m devbeats.main import-chords "%CHORD_FILE%" --title "%CHORD_TITLE%" --edit-if-missing --edit
echo.
pause
goto :menu

:python_missing
echo.
echo ERROR: Python no esta instalado o no aparece en PATH.
echo Instala Python 3.12 y vuelve a ejecutar este archivo.
pause
exit /b 1

:setup_failed
echo.
echo ERROR: No fue posible preparar DevBeats.
pause
exit /b 1

:end
endlocal
exit /b 0

