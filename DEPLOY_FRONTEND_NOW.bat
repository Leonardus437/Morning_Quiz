@echo off
echo ========================================
echo   Deploy Frontend with Review Feature
echo ========================================
echo.

cd /d "d:\Morning_Quiz-master\frontend"

echo [1/3] Building frontend...
call npm run build
if errorlevel 1 (
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo.
echo [2/3] Committing changes...
cd ..
git add .
git commit -m "Add Review Quiz feature - frontend API methods"

echo.
echo [3/3] Pushing to trigger Cloudflare deployment...
git push origin main

echo.
echo ========================================
echo   SUCCESS!
echo ========================================
echo.
echo Cloudflare Pages will rebuild in 2-3 minutes
echo Then check: https://tsskwizi.pages.dev/teacher
echo.
echo The "Pending Reviews" button should now work!
echo.
pause
