@echo off
setlocal EnableDelayedExpansion

echo ============================================================
echo   See-through - Launch WebUI
echo ============================================================
echo.

set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"
set "PROJECT_DIR=%SCRIPT_DIR%\see-through"
set "VENV_DIR=%PROJECT_DIR%\.venv"
set "WEBUI_DIR=%SCRIPT_DIR%\webui"
set "UV_DIR=%SCRIPT_DIR%\uv"
set "UV_EXE=%UV_DIR%\uv.exe"

if not exist "%VENV_DIR%" (
    echo ERROR: Virtual environment not found. Please run install_seethrough.bat first.
    pause
    exit /b 1
)

if not exist "%PROJECT_DIR%" (
    echo ERROR: Project not found. Please run install_seethrough.bat first.
    pause
    exit /b 1
)

where uv >nul 2>&1
if %errorlevel% equ 0 (
    set "UV_EXE=uv"
)

echo Ensuring Gradio is installed...
"%UV_EXE%" pip install --python "%VENV_DIR%\Scripts\python.exe" gradio

echo.
echo Launching See-through WebUI...
echo Open your browser to: http://127.0.0.1:7860
echo.

cd /d "%SCRIPT_DIR%"
call "%VENV_DIR%\Scripts\activate.bat"
set "PYTHONPATH=%SCRIPT_DIR%"
python webui\launch.py

pause
