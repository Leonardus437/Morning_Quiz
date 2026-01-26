@echo off
color 0E
echo.
echo ========================================
echo   CLOUDFLARE DEPLOYMENT - RETRY
echo ========================================
echo.
echo Previous deployment failed due to Cloudflare internal error
echo This script will retry with fresh build
echo.
echo ========================================
echo.

cd frontend

echo [1/4] Cleaning previous build...
if exist build rmdir /s /q build
if exist .svelte-kit rmdir /s /q .svelte-kit
echo Clean complete!

echo.
echo [2/4] Building fresh frontend...
call npm run build
if %errorlevel% neq 0 (
    color 0C
    echo.
    echo ERROR: Build failed!
    echo Check for syntax errors in your code
    echo.
    pause
    exit /b 1
)

echo.
echo [3/4] Deploying to Cloudflare Pages (Attempt 1)...
call npx wrangler pages deploy build --project-name=tsskwizi
if %errorlevel% equ 0 (
    goto success
)

echo.
echo Deployment failed. Waiting 10 seconds before retry...
timeout /t 10 /nobreak

echo.
echo [3/4] Deploying to Cloudflare Pages (Attempt 2)...
call npx wrangler pages deploy build --project-name=tsskwizi
if %errorlevel% equ 0 (
    goto success
)

echo.
echo Deployment failed again. Waiting 20 seconds before final retry...
timeout /t 20 /nobreak

echo.
echo [3/4] Deploying to Cloudflare Pages (Attempt 3 - Final)...
call npx wrangler pages deploy build --project-name=tsskwizi
if %errorlevel% equ 0 (
    goto success
)

:failure
color 0C
echo.
echo ========================================
echo   DEPLOYMENT FAILED
echo ========================================
echo.
echo All 3 attempts failed. This might be:
echo  1. Cloudflare internal issue (try again later)
echo  2. Wrangler authentication issue
echo  3. Project configuration issue
echo.
echo Troubleshooting steps:
echo  1. Check Cloudflare status: https://www.cloudflarestatus.com/
echo  2. Re-authenticate: npx wrangler login
echo  3. Check project name: tsskwizi
echo  4. Try manual deployment via Cloudflare dashboard
echo.
echo ========================================
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
echo Your fixes are now live:
echo  [x] Token expiration fixed
echo  [x] My Questions button restored
echo.
echo Test it now:
echo  1. https://tsskwizi.pages.dev/teacher
echo  2. Login: teacher001 / teacher123
echo  3. Click "My Questions" button
echo  4. Logout and re-login (no 401 errors!)
echo.
echo ========================================
echo.
pause
