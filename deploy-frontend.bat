@echo off
echo ========================================
echo CLOUDFLARE PAGES FRONTEND DEPLOYMENT
echo ========================================
echo.

cd /d "f:\SIDE HUSTLE\Morning_Quiz"

echo Step 1: Installing static adapter...
cd frontend
call npm install @sveltejs/adapter-static@^2.0.3

echo.
echo Step 2: Committing changes...
cd ..
git add frontend/package.json frontend/svelte.config.js
git commit -m "Configure frontend for Cloudflare Pages deployment"
git push origin master

echo.
echo ========================================
echo NEXT: Deploy on Cloudflare Pages
echo ========================================
echo.
echo 1. Go to: https://dash.cloudflare.com/
echo 2. Click "Workers & Pages" → "Create application" → "Pages"
echo 3. Connect to GitHub: Leonardus437/Morning_Quiz
echo 4. Configure build:
echo    - Project name: tvet-quiz-frontend
echo    - Build command: cd frontend ^&^& npm install ^&^& npm run build
echo    - Build output: frontend/build
echo    - Root directory: (leave empty)
echo 5. Add environment variable:
echo    - PUBLIC_API_URL = https://tvet-quiz-backend.onrender.com
echo 6. Click "Save and Deploy"
echo.
echo ========================================
pause
