@echo off
color 0E
echo.
echo ========================================
echo   CRITICAL FIX: Questions Visibility
echo ========================================
echo.
echo Fixes:
echo  [1] Remove created_by filter (show ALL questions)
echo  [2] Fix AI Parser upload (remove token check)
echo  [3] Stop notification spam on 401 errors
echo.

cd frontend
call npm run build
if %errorlevel% neq 0 (
    echo Build failed!
    pause
    exit /b 1
)

call npx wrangler pages deploy build --project-name=tsskwizi --skip-caching

color 0A
echo.
echo ========================================
echo   DEPLOYED!
echo ========================================
echo.
echo IMPORTANT: After deployment, you MUST:
echo  1. Logout completely
echo  2. Clear browser cache (Ctrl+Shift+Delete)
echo  3. Login again
echo  4. Then create questions
echo.
echo This ensures fresh token and no 401 errors.
echo.
pause
