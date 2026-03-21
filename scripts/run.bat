@echo off
title Multi-Agent Executor Launcher
color 0A
echo.
echo  ========================================
echo    🚀 MULTI-AGENT EXECUTOR
echo  ========================================
echo.
echo Starting Multi-Agent Executor System...
echo.
echo [1] Starting Backend Server...
echo [2] Checking Dependencies...
echo [3] Launching Web Interface...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.7+ first
    pause
    exit /b 1
)

REM Check if required packages are installed
echo Checking required packages...
python -c "import fastapi, uvicorn" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [INFO] Installing required packages...
    pip install fastapi uvicorn websockets python-multipart
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Failed to install packages
        pause
        exit /b 1
    )
)

REM Start the server
echo.
echo [SUCCESS] Starting server on http://localhost:8000
echo [INFO] Press Ctrl+C to stop the server
echo [INFO] Open your browser and navigate to: http://localhost:8000
echo.
echo ========================================

REM Change to the correct directory
cd /d "%~dp0"

REM Start the FastAPI server
python server.py

REM If server stops, wait for user input before closing
echo.
echo Server stopped. Press any key to exit...
pause >nul
