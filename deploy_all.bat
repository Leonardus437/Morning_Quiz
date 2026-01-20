@echo off
echo ========================================
echo Morning Quiz - Deploy to Production
echo ========================================
echo.

echo [1/3] Checking Git status...
git status
echo.

echo [2/3] Committing changes...
git add .
git commit -m "Deploy: Latest version %date% %time%"
echo.

echo [3/3] Pushing to Git (triggers auto-deploy)...
git push origin main
echo.

echo ========================================
echo Deployment Triggered!
echo ========================================
echo.
echo Cloudflare Pages: Auto-deploying from Git
echo Render Backend: Auto-deploying from Git
echo.
echo Check deployment status:
echo - Cloudflare: https://dash.cloudflare.com
echo - Render: https://dashboard.render.com
echo.
echo Wait 2-3 minutes for deployment to complete.
echo.
echo Test URLs:
echo - Frontend: https://tsskwizi.pages.dev
echo - Backend: https://tvet-quiz-backend.onrender.com/health
echo.
pause
