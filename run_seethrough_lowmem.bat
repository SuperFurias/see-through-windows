@echo off
setlocal EnableDelayedExpansion

echo ============================================================
echo   See-through - Run Inference (Low VRAM / Quantized CLI)
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

cd /d "%PROJECT_DIR%"
call "%VENV_DIR%\Scripts\activate.bat"

echo Installing bitsandbytes for quantization (if not installed)...
"%UV_EXE%" pip install --python "%VENV_DIR%\Scripts\python.exe" -r requirements-inference-bnb.txt 2>nul

if "%~1"=="" (
    set "INPUT_PATH=assets/test_image.png"
    echo No input specified. Using default: !INPUT_PATH!
) else (
    set "INPUT_PATH=%~1"
)

echo.
echo Running quantized See-through pipeline on: !INPUT_PATH!
echo This uses NF4 quantization for lower VRAM usage (~8GB).
echo.

python inference/scripts/inference_psd_quantized.py --srcp "!INPUT_PATH!" --save_to_psd

echo.
echo Done! Output saved to workspace/layerdiff_output/
echo.

if "%~1"=="" pause
