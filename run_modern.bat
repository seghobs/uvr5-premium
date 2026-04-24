@echo off
setlocal enabledelayedexpansion
title UVR5 Premium UI Launcher

echo Starting UVR5 Premium UI...
echo.

if exist "env\python.exe" (
    set "PYTHON_EXE=env\python.exe"
) else (
    set "PYTHON_EXE=python"
)

echo Using Python: !PYTHON_EXE!
echo.

echo Launching FastAPI server on http://localhost:8000
echo.

!PYTHON_EXE! api_modern.py

pause
