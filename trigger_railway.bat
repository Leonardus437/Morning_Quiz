@echo off
echo ========================================
echo Triggering Railway Deployment
echo ========================================

git commit --allow-empty -m "Deploy assignment system with trade/level filtering"
git push origin master

echo.
echo ========================================
echo Done! Check Railway dashboard for deployment
echo ========================================
pause
