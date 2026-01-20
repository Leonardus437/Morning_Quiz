@echo off
echo ========================================
echo Deploying to GitLab for Cloudflare Pages
echo ========================================
echo.

cd frontend

echo Checking GitLab remote...
git remote -v

echo.
echo Adding GitLab remote if not exists...
git remote add gitlab https://gitlab.com/Leonardus437/Morning_Quiz.git 2>nul

echo.
echo Pushing to GitLab...
git push gitlab master --force

echo.
echo ========================================
echo Done! Check Cloudflare Pages dashboard
echo ========================================
pause
