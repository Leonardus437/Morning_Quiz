@echo off
echo ========================================
echo   Deploy Review Quiz Feature
echo ========================================
echo.

echo [1/5] Checking current directory...
cd /d "%~dp0"
echo Current directory: %CD%
echo.

echo [2/5] Building frontend for production...
cd frontend
call npm run build
if errorlevel 1 (
    echo ERROR: Frontend build failed!
    pause
    exit /b 1
)
echo Frontend build successful!
echo.

echo [3/5] Checking Git status...
cd ..
git status
echo.

echo [4/5] Committing changes...
git add .
git commit -m "Deploy Review Quiz feature - All teacher dashboard features working"
if errorlevel 1 (
    echo No changes to commit or commit failed
)
echo.

echo [5/5] Pushing to repository...
git push origin main
if errorlevel 1 (
    echo ERROR: Git push failed!
    echo Please check your Git credentials and try again.
    pause
    exit /b 1
)
echo.

echo ========================================
echo   Deployment Complete!
echo ========================================
echo.
echo Your changes have been pushed to Git.
echo Cloudflare Pages will automatically rebuild and deploy.
echo.
echo Check deployment status at:
echo https://dash.cloudflare.com/pages
echo.
echo Your site will be live at:
echo https://tsskwizi.pages.dev/teacher
echo.
echo Wait 2-3 minutes for Cloudflare to rebuild.
echo Then test the Review Quiz feature!
echo.
pause
