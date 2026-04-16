@echo off
REM Common setup for all run scripts
REM This file is called by other batch files - do not use setlocal here

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

where uv >nul 2>&1
if %errorlevel% equ 0 (
    set "UV_EXE=uv"
) else (
    set "UV_DIR=%SCRIPT_DIR%\uv"
    set "UV_EXE=%UV_DIR%\uv.exe"
)
