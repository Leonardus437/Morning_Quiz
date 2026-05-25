@echo off
echo ========================================
echo Railway API Deployment Script
echo ========================================
echo.

REM Check if token is set
if "%RAILWAY_TOKEN%"=="" (
    echo ERROR: RAILWAY_TOKEN not set!
    echo.
    echo Please set your Railway API token first:
    echo   set RAILWAY_TOKEN=your_token_here
    echo.
    echo Get token from: https://railway.app/account/tokens
    echo.
    pause
    exit /b 1
)

cd /d c:\Users\Hp\Documents\Morning_Quiz-master\backend

echo Step 1: Pushing to GitHub...
git add .
git commit -m "Deploy: %date% %time%"
git push origin master

echo.
echo Step 2: Triggering Railway deployment via API...
python railway_deploy.py

echo.
echo Done! Check Railway dashboard for deployment progress.
pause
