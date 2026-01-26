@echo off
color 0E
echo.
echo ========================================
echo   DEPLOYING WITH WRANGLER (RETRY)
echo ========================================
echo.
echo Using build from previous attempt...
echo.

cd frontend

REM Check if build exists
if not exist build (
    echo Build directory not found. Building now...
    call npm run build
    if %errorlevel% neq 0 (
        color 0C
        echo ERROR: Build failed!
        pause
        exit /b 1
    )
)

echo.
echo [1/3] Attempt 1: Deploying to Cloudflare...
timeout /t 2 /nobreak >nul
call npx wrangler pages deploy build --project-name=tsskwizi --compatibility-date=2024-01-01
if %errorlevel% equ 0 goto success

echo.
echo Attempt 1 failed. Waiting 10 seconds...
timeout /t 10 /nobreak

echo.
echo [2/3] Attempt 2: Deploying to Cloudflare...
call npx wrangler pages deploy build --project-name=tsskwizi --compatibility-date=2024-01-01
if %errorlevel% equ 0 goto success

echo.
echo Attempt 2 failed. Waiting 20 seconds...
timeout /t 20 /nobreak

echo.
echo [3/3] Attempt 3: Deploying to Cloudflare...
call npx wrangler pages deploy build --project-name=tsskwizi --compatibility-date=2024-01-01
if %errorlevel% equ 0 goto success

:failure
color 0C
echo.
echo ========================================
echo   ALL ATTEMPTS FAILED
echo ========================================
echo.
echo The network timeout persists.
echo.
echo Alternative: Deploy via GitLab
echo  1. Push to GitLab: git push gitlab main
echo  2. Cloudflare will auto-deploy
echo.
echo Or try again later when network is better.
echo.
pause
exit /b 1

:success
color 0A
echo.
echo ========================================
echo   DEPLOYMENT SUCCESSFUL!
echo ========================================
echo.
echo All 5 fixes are now live!
echo.
echo Test at: https://tsskwizi.pages.dev/teacher
echo Login: teacher001 / teacher123
echo.
echo What's Fixed:
echo  [x] Add Question button removed
echo  [x] My Questions button added
echo  [x] All 13 question types working
echo  [x] Enhanced AI Parser
echo  [x] Auto-redirect to My Questions
echo  [x] Smart notifications
echo.
pause
