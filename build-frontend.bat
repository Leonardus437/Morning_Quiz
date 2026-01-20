@echo off
echo ========================================
echo BUILDING FRONTEND FOR CLOUDFLARE
echo ========================================
echo.

cd /d "f:\SIDE HUSTLE\Morning_Quiz\frontend"

echo Step 1: Installing dependencies...
call npm install

echo.
echo Step 2: Installing static adapter...
call npm install @sveltejs/adapter-static@^2.0.3

echo.
echo Step 3: Building frontend...
call npm run build

echo.
echo ========================================
echo BUILD COMPLETE!
echo ========================================
echo.
echo Your frontend is ready in: frontend\build
echo.
echo NEXT STEPS:
echo 1. Go to: https://dash.cloudflare.com/pages
echo 2. Click "Upload assets"
echo 3. Drag and drop the "frontend\build" folder
echo 4. Project name: tvet-quiz-frontend
echo 5. Click "Deploy site"
echo.
echo After deployment, add environment variable:
echo - PUBLIC_API_URL = https://tvet-quiz-backend.onrender.com
echo.
pause
