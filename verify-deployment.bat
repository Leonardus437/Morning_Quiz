@echo off
echo ========================================
echo DEPLOYMENT VERIFICATION
echo ========================================
echo.

echo [1/4] Checking GitLab last commit...
git log -1 --oneline
echo.

echo [2/4] Checking GitHub last commit...
git ls-remote origin HEAD
echo.

echo [3/4] Checking GitLab remote...
git ls-remote gitlab HEAD
echo.

echo [4/4] Testing live site...
curl -s -I https://tsskwizi.pages.dev | findstr "HTTP"
echo.

echo ========================================
echo DEPLOYMENT STATUS
echo ========================================
echo Frontend (Cloudflare): https://tsskwizi.pages.dev
echo Backend (Render): https://tvet-quiz-backend.onrender.com
echo.
echo Wait 2-3 minutes for Cloudflare Pages to build and deploy.
echo Then visit: https://tsskwizi.pages.dev
echo.
pause
