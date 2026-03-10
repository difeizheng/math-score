@echo off
chcp 65001 >nul
echo ========================================
echo   Math Score System - Backend
echo ========================================
echo.

cd /d "%~dp0backend"

echo [1/2] Check Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found
    pause
    exit /b 1
)
echo OK: Python found

echo.
echo [2/2] Starting backend service...
echo.
echo API: http://localhost:8808
echo Docs: http://localhost:8808/docs
echo.
echo Press Ctrl+C to stop
echo.

python main.py

pause
