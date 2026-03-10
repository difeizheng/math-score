@echo off
chcp 65001 >nul
echo ========================================
echo   Math Score System - Frontend
echo ========================================
echo.

cd /d "%~dp0frontend"

echo [1/2] Check Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found
    pause
    exit /b 1
)
echo OK: Python found

echo.
echo [2/2] Starting frontend server...
echo.
echo URL: http://localhost:3000
echo.
echo Press Ctrl+C to stop
echo.
echo Tip: Or open index.html directly in browser
echo.

python -m http.server 3000

pause
