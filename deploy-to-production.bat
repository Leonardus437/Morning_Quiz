@echo off
echo ========================================
echo   TVET Quiz - Production Deployment
echo ========================================
echo.

echo [1/4] Checking Git status...
git status
echo.

echo [2/4] Adding all changes...
git add .
echo.

echo [3/4] Committing changes...
git commit -m "Add comprehensive anti-cheating system with fullscreen lock, tab/window detection, copy/paste prevention, three-strike warnings, auto-submit, and teacher notifications"
echo.

echo [4/4] Pushing to GitHub...
git push origin main
echo.

echo ========================================
echo   Deployment Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Cloudflare Pages will auto-deploy frontend
echo 2. Check: https://dash.cloudflare.com/86089f0bb941af81d975a82b892fe038/pages/view/tsskwizi
echo 3. Verify backend: https://tvet-quiz-backend.onrender.com/health
echo 4. Test site: https://tsskwizi.pages.dev
echo.
echo Press any key to exit...
pause >nul
