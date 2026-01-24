@echo off
echo ========================================
echo  Deploy TVET Quiz System
echo ========================================
echo.
echo Backend: Render.com (already deployed)
echo Frontend: Cloudflare Pages (tsskwizi.pages.dev)
echo.

REM Check git status
git remote -v | findstr origin >nul
if errorlevel 1 (
    echo Setting up GitHub remote...
    git remote add origin https://github.com/Leonardus437/Morning_Quiz.git
)

echo.
echo Step 1: Committing changes...
git add .
git commit -m "Deploy to production - Backend: Render, Frontend: Cloudflare Pages"

echo.
echo Step 2: Pushing to GitHub...
git push -u origin main

echo.
echo Step 3: Deploying frontend to Cloudflare Pages...
cd frontend
call npm install
call npm run build
call npx wrangler pages deploy build --project-name=tsskwizi

echo.
echo ========================================
echo  Deployment Complete!
echo ========================================
echo.
echo Backend: https://tvet-quiz-backend.onrender.com
echo Frontend: https://tsskwizi.pages.dev
echo.
pause
