@echo off
setlocal EnableDelayedExpansion

echo ============================================================
echo   See-through - Launch Qt UI (Live2D Annotation)
echo ============================================================
echo.

set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"
set "PROJECT_DIR=%SCRIPT_DIR%\see-through"
set "VENV_DIR=%PROJECT_DIR%\.venv"

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

cd /d "%PROJECT_DIR%"
call "%VENV_DIR%\Scripts\activate.bat"

echo Launching See-through Qt UI...
echo.

python ui/ui/launch.py %*

echo.
pause
