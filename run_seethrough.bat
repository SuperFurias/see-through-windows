@echo off
setlocal EnableDelayedExpansion

call "%~dp0common_setup.bat"

cd /d "%PROJECT_DIR%"
call "%VENV_DIR%\Scripts\activate.bat"

echo Launching See-through Qt UI...
echo.

python ui/ui/launch.py %*

echo.
pause
