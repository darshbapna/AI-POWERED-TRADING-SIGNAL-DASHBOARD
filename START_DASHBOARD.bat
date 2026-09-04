@echo off
title AURA QUANT - AI Trading Signal Dashboard
color 0A
echo =====================================================
echo   Starting AI Trading Signal Dashboard Terminal...
echo =====================================================
echo
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not added to PATH.
    echo Please install Python 3.10+ from https://www.python.org/
    pause
    exit /b
)
echo [1/3] Checking dependencies...
pip install -r requirements.txt
echo [2/3] Starting backend server and live WebSockets...
start "AURA QUANT Backend" python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
timeout /t 3 /nobreak >nul
echo [3/3] Opening Dashboard in your browser...
start http://localhost:8000/
echo
echo =====================================================
echo   Dashboard is running at: http://localhost:8000/
echo =====================================================
