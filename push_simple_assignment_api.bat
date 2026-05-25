@echo off
cd /d c:\Users\Hp\Documents\Morning_Quiz-master\backend

echo Pushing simplified assignment API...
git add assignment_api_simple.py main.py
git commit -m "Fix: Use synchronous assignment API compatible with existing database"
git push origin master

echo.
echo ========================================
echo PUSHED TO GITHUB!
echo ========================================
echo.
echo Railway will auto-deploy in 2-3 minutes (if webhook works)
echo OR manually deploy: https://railway.com/project/477122d8-1d79-437f-8513-5bb901527f41/service/ce549504-cde6-4d20-a142-01dc10f54b5f/deployments
echo.
echo After deploy, test:
echo https://web-production-2c325.up.railway.app/api/assignments/assignments
echo.
pause
