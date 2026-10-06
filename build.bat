@echo off
REM ============================================================
REM  build.bat ? PDF Master
REM  Compila la aplicacion en un .exe usando PyInstaller
REM ============================================================
SETLOCAL ENABLEDELAYEDEXPANSION

SET APP_NAME=PDF Master
SET SPEC_FILE=PDF Master.spec
SET DIST_DIR=dist
SET BUILD_DIR=build
SET VENV=venv\Scripts

echo.
echo ==========================================
echo  %APP_NAME% ? Script de compilacion
echo ==========================================
echo.

REM ?? 1. Verificar entorno virtual ??????????????????????????????
IF NOT EXIST "%VENV%\python.exe" (
    echo ERROR: No se encontro el entorno virtual en .\venv\
    echo Crea el entorno con:  python -m venv venv
    echo Luego instala:        venv\Scripts\pip install -r requirements.txt
    pause
    exit /b 1
)

REM ?? 2. Verificar PyInstaller ???????????????????????????????????
"%VENV%\python.exe" -c "import PyInstaller" 2>nul
IF ERRORLEVEL 1 (
    echo Instalando PyInstaller...
    "%VENV%\pip.exe" install pyinstaller>=6.0.0
)

REM ?? 3. Limpiar builds anteriores ??????????????????????????????
echo Limpiando builds anteriores...
IF EXIST "%BUILD_DIR%" RMDIR /S /Q "%BUILD_DIR%"
IF EXIST "%DIST_DIR%\%APP_NAME%" RMDIR /S /Q "%DIST_DIR%\%APP_NAME%"

REM ?? 4. Compilar ???????????????????????????????????????????????
echo Compilando "%APP_NAME%"...
echo.
"%VENV%\pyinstaller.exe" "%SPEC_FILE%" --noconfirm --clean

IF ERRORLEVEL 1 (
    echo.
    echo ERROR: La compilacion fallo. Revisa los mensajes anteriores.
    pause
    exit /b 1
)

REM ?? 5. Copiar archivos extra al directorio de distribucion ?????
SET OUT_DIR=%DIST_DIR%\%APP_NAME%

echo.
echo Copiando archivos adicionales...
IF EXIST "install_context_menu.py"   COPY /Y "install_context_menu.py"   "%OUT_DIR%\" >nul
IF EXIST "uninstall_context_menu.py" COPY /Y "uninstall_context_menu.py" "%OUT_DIR%\" >nul
IF EXIST "README.md"                 COPY /Y "README.md"                 "%OUT_DIR%\" >nul

REM ?? 6. Resultado ??????????????????????????????????????????????
echo.
echo ==========================================
echo  Compilacion completada exitosamente!
echo  Distribuible: %OUT_DIR%\
echo ==========================================
echo.

start "" explorer "%OUT_DIR%"
pause
