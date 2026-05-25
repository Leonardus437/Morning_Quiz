@echo off
cd /d "%~dp0"
git commit --allow-empty -m "Trigger Railway deployment"
git push origin master
echo.
echo Deployment triggered! Check Railway dashboard in 1-2 minutes.
pause
