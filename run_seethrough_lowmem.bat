@echo off
setlocal EnableDelayedExpansion

call "%~dp0common_setup.bat"

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
