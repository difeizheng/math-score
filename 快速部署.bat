@echo off
chcp 65001 >nul
echo ========================================
echo   Math Score System - Quick Deploy
echo ========================================
echo.

cd /d "%~dp0"

echo [1/4] Checking Git...
git --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Git not installed
    echo Download: https://git-scm.com/downloads
    pause
    exit /b 1
)
echo [OK] Git installed

echo.
echo [2/4] Initialize Git repo...
if not exist ".git" (
    git init
    echo [OK] Git repo initialized
) else (
    echo [OK] Git repo exists
)

echo.
echo [3/4] Adding files...
git add .
echo [OK] Files added

echo.
echo [4/4] Creating first commit...
git commit -m "Initial commit - Math Score System" >nul 2>&1
if errorlevel 1 (
    echo [INFO] No changes or already committed
) else (
    echo [OK] First commit created
)

echo.
echo ========================================
echo   Deploy Ready!
echo ========================================
echo.
echo Next Steps:
echo.
echo 1. Create GitHub repo
echo    Visit: https://github.com/new
echo    Repo name: math-score
echo.
echo 2. Link remote repo
echo    Run (replace YOUR_USERNAME):
echo    git remote add origin https://github.com/YOUR_USERNAME/math-score.git
echo    git push -u origin main
echo.
echo 3. Deploy backend to Render
echo    Visit: https://render.com
echo    See: DEPLOYMENT_GUIDE.md
echo.
echo 4. Deploy frontend to Vercel
echo    Visit: https://vercel.com
echo    See: DEPLOYMENT_GUIDE.md
echo.

pause
