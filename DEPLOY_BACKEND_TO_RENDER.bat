@echo off
color 0E
echo.
echo ========================================
echo   DEPLOYING BACKEND TO RENDER
echo ========================================
echo.
echo This will:
echo  1. Commit backend changes
echo  2. Push to GitLab
echo  3. Trigger Render auto-deploy
echo.
echo ========================================
echo.

echo [1/3] Committing backend changes...
git add backend/
git commit -m "Fix: Increase token expiration to 24 hours, fix 401 errors"

echo.
echo [2/3] Pushing to GitLab...
git push origin main

if %errorlevel% neq 0 (
    echo.
    echo Trying 'gitlab' remote...
    git push gitlab main
)

echo.
color 0A
echo ========================================
echo   BACKEND DEPLOYMENT TRIGGERED!
echo ========================================
echo.
echo Render will now rebuild your backend.
echo.
echo Wait 3-5 minutes, then:
echo  1. Clear browser cache (Ctrl+Shift+Delete)
echo  2. Go to: https://tsskwizi.pages.dev/teacher
echo  3. Login fresh
echo  4. Create questions
echo  5. They WILL appear!
echo.
echo Check deployment status:
echo  https://dashboard.render.com/
echo.
pause
