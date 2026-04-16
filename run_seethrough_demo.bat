@echo off
setlocal EnableDelayedExpansion

call "%~dp0common_setup.bat"

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
