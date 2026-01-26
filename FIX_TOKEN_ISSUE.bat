@echo off
color 0E
echo.
echo ========================================
echo   FIXING TOKEN EXPIRATION ISSUE
echo ========================================
echo.
echo Issue: "Invalid token. Please login again" after re-login
echo.
echo Fix Applied:
echo  [x] Token now syncs from localStorage BEFORE every request
echo  [x] Token persistence double-verified after login
echo  [x] Smarter 401 handling (checks for fresh token first)
echo  [x] Prevents premature token clearing
echo.
echo ========================================
echo.

cd frontend

echo [1/3] Building frontend with fix...
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
echo   TOKEN FIX DEPLOYED!
echo ========================================
echo.
echo Test it now:
echo  1. Go to: https://tsskwizi.pages.dev/teacher
echo  2. Login with: teacher001 / teacher123
echo  3. Navigate to any page (Lessons, Question Types, etc.)
echo  4. Logout and re-login
echo  5. Navigate again - should work without 401 errors!
echo.
echo What was fixed:
echo  - Token is now synced from localStorage at the START of every request
echo  - Login now double-verifies token is saved
echo  - 401 errors check for fresh token before clearing
echo  - Prevents token loss during navigation
echo.
echo ========================================
echo.
pause
