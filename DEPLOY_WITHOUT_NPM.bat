@echo off
color 0A
echo.
echo ========================================
echo   DEPLOY FRONTEND TO CLOUDFLARE
echo ========================================
echo.
echo OPTION 1: Install Node.js (Recommended)
echo ----------------------------------------
echo 1. Download: https://nodejs.org/
echo 2. Install Node.js (LTS version)
echo 3. Restart this terminal
echo 4. Run: cd frontend ^&^& npm run build
echo.
echo ========================================
echo.
echo OPTION 2: Manual Upload (NO Node.js needed)
echo --------------------------------------------
echo.
echo Your frontend is ALREADY BUILT in Docker!
echo.
echo STEP 1: Copy build from Docker container
docker cp tvet_quiz-frontend-1:/app/build ./frontend-build
echo.
if exist "frontend-build" (
    echo ✅ Build copied successfully!
    echo.
    echo STEP 2: Upload to Cloudflare
    echo 1. Go to: https://dash.cloudflare.com/86089f0bb941af81d975a82b892fe038/pages/view/tsskwizi
    echo 2. Click "Create deployment"
    echo 3. Drag the "frontend-build" folder
    echo 4. Done!
    echo.
    echo Build folder location: %cd%\frontend-build
    echo.
    explorer frontend-build
) else (
    echo ❌ Docker container not running
    echo.
    echo Start Docker first:
    echo   docker-compose up -d
    echo.
    echo Then run this script again
)
echo.
pause
