@echo off
echo ========================================
echo PUSHING LATEST FRONTEND TO GITLAB
echo ========================================
echo.

cd /d "f:\SIDE HUSTLE\Morning_Quiz"

echo Step 1: Adding all changes...
git add -A

echo Step 2: Committing...
git commit -m "Update frontend to latest version with current index page"

echo Step 3: Pushing to GitLab...
git push gitlab master:main --force

echo.
echo ========================================
echo DONE! Cloudflare will auto-deploy in 2-3 minutes
echo ========================================
echo.
echo Check deployment at: https://dash.cloudflare.com/
echo Your site: https://tsskwizi.pages.dev/
echo.
pause
