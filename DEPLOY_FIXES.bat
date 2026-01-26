@echo off
color 0B
echo.
echo ========================================
echo   DEPLOYING FIXES
echo ========================================
echo.
echo Fixes included:
echo  [x] Token expiration issue (401 after re-login)
echo  [x] My Questions button restored in navigation
echo.
echo ========================================
echo.

cd frontend

echo [1/3] Building frontend...
call npm run build
if %errorlevel% neq 0 (
    color 0C
    echo.
    echo ERROR: Build failed!
    echo.
    pause
    exit /b 1
)

echo.
echo [2/3] Deploying to Cloudflare Pages...
call npx wrangler pages deploy build --project-name=tsskwizi

echo.
color 0A
echo ========================================
echo   DEPLOYMENT COMPLETE!
echo ========================================
echo.
echo Test it now:
echo  1. Go to: https://tsskwizi.pages.dev/teacher
echo  2. Login with: teacher001 / teacher123
echo  3. You should see "My Questions" button in navigation
echo  4. Logout and re-login - no more 401 errors!
echo.
echo What was fixed:
echo  - Token now syncs from localStorage before every request
echo  - My Questions button added to main navigation
echo  - Smarter 401 error handling
echo  - Better token persistence
echo.
echo ========================================
echo.
pause
