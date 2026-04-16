@echo off
setlocal EnableDelayedExpansion

call "%~dp0common_setup.bat"

set "WEBUI_DIR=%SCRIPT_DIR%\webui"

echo.
echo Launching See-through WebUI...
echo.

cd /d "%SCRIPT_DIR%"
call "%VENV_DIR%\Scripts\activate.bat"
set "PYTHONPATH=%SCRIPT_DIR%"
python webui\launch.py

pause
