@echo off
setlocal
cd /d "%~dp0"

python --version >NUL 2>&1
if errorlevel 1 (
    py -3.11 --version >NUL 2>&1 || (echo [ERROR] Instala Python 3.11. & pause & exit /b 1)
    set "PY=py -3.11"
) else (
    set "PY=python"
)

if not exist ".venv\Scripts\python.exe" (
    %PY% -m venv .venv
)
call ".venv\Scripts\activate"
python -m pip install --upgrade pip
if exist "requirements.txt" (
    pip install -r requirements.txt
) else (
    pip install reportlab==4.4.3 openpyxl==3.1.5
)

python main.py
endlocal
