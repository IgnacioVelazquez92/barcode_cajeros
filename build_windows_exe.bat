@echo off
setlocal enabledelayedexpansion

echo ===============================================
echo  Build: Gestor de Credenciales (Windows .exe)
echo ===============================================
cd /d "%~dp0"

REM 1) Detectar Python 3.11
python --version >NUL 2>&1
if errorlevel 1 (
    echo [INFO] Python no encontrado en PATH, probando con "py -3.11"...
    py -3.11 --version >NUL 2>&1
    if errorlevel 1 (
        echo [ERROR] No se encontro Python 3.11. Instalala y agregala al PATH.
        pause
        exit /b 1
    )
    set "PY=py -3.11"
) else (
    set "PY=python"
)

REM 2) Crear venv si no existe
if not exist ".venv\Scripts\python.exe" (
    echo [STEP] Creando entorno virtual .venv ...
    %PY% -m venv .venv
)

REM 3) Activar venv
call ".venv\Scripts\activate"

REM 4) Actualizar pip e instalar dependencias
echo [STEP] Actualizando pip...
python -m pip install --upgrade pip

if exist "requirements.txt" (
    echo [STEP] Instalando requirements.txt ...
    pip install -r requirements.txt
) else (
    echo [WARN] NO hay requirements.txt. Instalando minimos...
    pip install reportlab==4.4.3 openpyxl==3.1.5
)

echo [STEP] Instalando PyInstaller...
pip install --upgrade pyinstaller

REM 5) Hooks personalizados para ReportLab (imports dinamicos)
if not exist "hooks" mkdir "hooks"
(
echo hiddenimports = [
echo     'reportlab.graphics.barcode.code128',
echo     'reportlab.graphics.barcode.code39',
echo     'reportlab.graphics.barcode.code93',
echo     'reportlab.graphics.barcode.eanbc',
echo     'reportlab.graphics.barcode.usps',
echo     'reportlab.graphics.barcode.qr',
echo     'reportlab.graphics.barcode.msi',
echo     'reportlab.graphics.barcode.codabar',
echo ]
) > "hooks\hook-reportlab.graphics.barcode.py"

REM 6) Limpiar salidas anteriores
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "GestorCredenciales.spec" del /q "GestorCredenciales.spec"

REM 7) Icono (opcional)
set "ICON_SWITCH="
if exist "icono.ico" set "ICON_SWITCH=--icon icono.ico"

REM 8) Ejecutar PyInstaller
echo [STEP] Ejecutando PyInstaller...

pyinstaller ^
 --noconfirm ^
 --clean ^
 --onefile ^
 --windowed ^
 %ICON_SWITCH% ^
 --name "GestorCredenciales" ^
 --additional-hooks-dir hooks ^
 --collect-submodules reportlab.graphics.barcode ^
 --collect-submodules reportlab.pdfbase ^
 --collect-data reportlab ^
 main.py

if errorlevel 1 (
    echo [ERROR] Fallo el empaquetado.
    pause
    exit /b 1
)

echo.
echo [OK] Ejecutable creado: dist\GestorCredenciales.exe
echo.

REM 9) Crear acceso directo en el Escritorio
for /f "usebackq delims=" %%D in (`powershell -NoProfile -Command "[Environment]::GetFolderPath('Desktop')"`) do set "DESKTOP=%%D"

if exist "%DESKTOP%\GestorCredenciales.lnk" del "%DESKTOP%\GestorCredenciales.lnk"

if exist "icono.ico" (
  powershell -NoProfile -Command ^
    "$desktop=[Environment]::GetFolderPath('Desktop');" ^
    "$lnk=Join-Path $desktop 'GestorCredenciales.lnk';" ^
    "$ws=New-Object -ComObject WScript.Shell;" ^
    "$s=$ws.CreateShortcut($lnk);" ^
    "$s.TargetPath='$pwd\dist\GestorCredenciales.exe';" ^
    "$s.WorkingDirectory='$pwd\dist';" ^
    "$s.IconLocation='$pwd\icono.ico';" ^
    "$s.Save()"
) else (
  powershell -NoProfile -Command ^
    "$desktop=[Environment]::GetFolderPath('Desktop');" ^
    "$lnk=Join-Path $desktop 'GestorCredenciales.lnk';" ^
    "$ws=New-Object -ComObject WScript.Shell;" ^
    "$s=$ws.CreateShortcut($lnk);" ^
    "$s.TargetPath='$pwd\dist\GestorCredenciales.exe';" ^
    "$s.WorkingDirectory='$pwd\dist';" ^
    "$s.Save()"
)

REM 10) Abrir carpeta dist
explorer "%cd%\dist"

endlocal
