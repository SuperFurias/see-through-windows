@echo off
setlocal EnableDelayedExpansion

echo ============================================================
echo   See-through Portable Installer (using uv)
echo   Downloads and sets up everything needed to run the project
echo ============================================================
echo.

set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"
set "PROJECT_DIR=%SCRIPT_DIR%\see-through"
set "VENV_DIR=%PROJECT_DIR%\.venv"
set "UV_DIR=%SCRIPT_DIR%\uv"
set "UV_EXE=%UV_DIR%\uv.exe"
set "UV_VERSION=0.5.29"
set "UV_URL=https://github.com/astral-sh/uv/releases/download/%UV_VERSION%/uv-x86_64-pc-windows-msvc.zip"

echo Checking for Git...
where git >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Git is already installed on the system.
    set "GIT_CMD=git"
) else (
    echo [ERROR] Git is required but not installed.
    echo Please install Git from https://git-scm.com/download/win
    pause
    exit /b 1
)

echo.
echo Checking for uv (fast Python package manager)...
where uv >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] uv is already installed on the system.
    set "UV_EXE=uv"
) else (
    echo [INSTALL] uv not found. Installing portable uv...
    if not exist "%UV_DIR%" (
        echo Downloading portable uv...
        powershell -Command "Invoke-WebRequest -Uri '%UV_URL%' -OutFile '%SCRIPT_DIR%\uv.zip'"
        echo Extracting portable uv...
        powershell -Command "Expand-Archive -Path '%SCRIPT_DIR%\uv.zip' -DestinationPath '%UV_DIR%' -Force"
        del "%SCRIPT_DIR%\uv.zip"
        echo [OK] Portable uv installed.
    ) else (
        echo [OK] Portable uv already exists.
    )
)

echo.
echo Cloning see-through repository...
if not exist "%PROJECT_DIR%" (
    "%GIT_CMD%" clone https://github.com/shitagaki-lab/see-through.git "%PROJECT_DIR%"
    echo [OK] Repository cloned.
) else (
    echo [OK] Repository already exists. Updating...
    cd /d "%PROJECT_DIR%"
    "%GIT_CMD%" pull
    cd /d "%SCRIPT_DIR%"
)

echo.
echo Creating virtual environment with Python 3.12 using uv...
cd /d "%PROJECT_DIR%"
if not exist "%VENV_DIR%" (
    "%UV_EXE%" venv --python 3.12
    echo [OK] Virtual environment created.
) else (
    echo [OK] Virtual environment already exists.
)

echo.
echo Installing PyTorch with CUDA 12.8 support...
"%UV_EXE%" pip install torch==2.8.0+cu128 torchvision==0.23.0+cu128 torchaudio==2.8.0+cu128 --index-url https://download.pytorch.org/whl/cu128

echo.
echo Installing main requirements...
"%UV_EXE%" pip install -r requirements.txt

echo.
echo Installing mmcv/mmdet (Windows prebuilt wheels)...
echo mmcv requires compilation on Windows. Installing prebuilt wheel if available...
"%UV_EXE%" pip install mmcv==2.1.0 -f https://download.openmmlab.com/mmcv/dist/cu128/torch2.8/index.html 2>nul
if %errorlevel% neq 0 (
    echo [WARN] mmcv prebuilt wheel not found, trying without CUDA...
    "%UV_EXE%" pip install mmcv==2.1.0 -f https://download.openmmlab.com/mmcv/dist/cpu/torch2.8/index.html 2>nul
)
"%UV_EXE%" pip install mmengine==0.10.7 mmdet==3.3.0

echo.
echo Installing annotators requirements (skipping uvloop on Windows)...
"%UV_EXE%" pip install --no-build-isolation detectron2 -f https://dl.fbaipublicfiles.com/detectron2/wheels/cu128/torch2.8/index.html 2>nul
if %errorlevel% neq 0 (
    echo [WARN] detectron2 prebuilt wheel not found, trying from source...
    "%UV_EXE%" pip install --no-build-isolation "detectron2 @ git+https://github.com/facebookresearch/detectron2@a25898a09d6ee232767647e92c6177fb1c642369" 2>nul
)
"%UV_EXE%" pip install hydra-core pydantic>=2.9.2

echo.
echo Installing SAM2...
"%UV_EXE%" pip install --no-build-isolation "sam-2 @ git+https://github.com/facebookresearch/segment-anything-2@c2ec8e14a185632b0a5d8b161928ceb50197eddc" 2>nul

echo.
echo Installing bnb requirements (for low VRAM)...
"%UV_EXE%" pip install -r requirements-inference-bnb.txt 2>nul

echo.
echo Installing WebUI dependencies...
"%UV_EXE%" pip install gradio

echo.
echo Creating assets symlink...
if not exist "%PROJECT_DIR%\assets" (
    if exist "%PROJECT_DIR%\common\assets" (
        mklink /D "%PROJECT_DIR%\assets" "%PROJECT_DIR%\common\assets"
    )
)

echo.
echo ============================================================
echo   Installation Complete!
echo ============================================================
echo.
echo Project location: %PROJECT_DIR%
echo.
echo Run the WebUI:
echo   run_seethrough_webui.bat
echo.
echo Run CLI inference:
echo   run_seethrough_cli.bat image.png
echo.
echo Run CLI inference (low VRAM):
echo   run_seethrough_lowmem.bat image.png
echo.

pause
