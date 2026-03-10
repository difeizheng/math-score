@echo off
chcp 65001 >nul
echo ========================================
echo   Math Score System - Install Dependencies
echo ========================================
echo.

cd /d "%~dp0backend"

echo [1/2] Check Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found
    echo Download: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo OK: Python found

echo.
echo [2/2] Installing Python packages...
echo.

pip install -r requirements.txt

echo.
echo ========================================
echo   Done!
echo ========================================
echo.
echo Next steps:
echo 1. Double click: qidong-houduan.bat
echo 2. Double click: qidong-qianduan.bat
echo 3. Open browser: http://localhost:3000
echo.

pause
