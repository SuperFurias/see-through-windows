@echo off
setlocal EnableDelayedExpansion

echo ============================================================
echo   See-through - Launch Jupyter Demo
echo ============================================================
echo.

set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"
set "PROJECT_DIR=%SCRIPT_DIR%\see-through"
set "VENV_DIR=%PROJECT_DIR%\.venv"
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

echo Installing Jupyter...
"%UV_EXE%" pip install --python "%VENV_DIR%\Scripts\python.exe" jupyter ipywidgets

echo.
echo Launching Jupyter Notebook...
echo Demo notebook: inference/demo/bodypartseg_sam.ipynb
echo.

cd /d "%PROJECT_DIR%"

start "Jupyter Notebook" cmd /k "call "%VENV_DIR%\Scripts\activate.bat" && python -m notebook --notebook-dir="%PROJECT_DIR%\inference\demo""

echo.
echo Jupyter Notebook server started in a new window.
echo A browser window should open automatically.
echo Close the Jupyter window when done.
echo.

pause
