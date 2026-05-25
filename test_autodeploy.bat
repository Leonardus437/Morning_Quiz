@echo off
cd /d c:\Users\Hp\Documents\Morning_Quiz-master\backend

echo Creating test commit to verify auto-deploy...
git commit --allow-empty -m "Test auto-deploy after webhook reconnection"
git push origin master

echo.
echo Test commit pushed!
echo.
echo Check Railway Deployments in 1 minute:
echo https://railway.com/project/477122d8-1d79-437f-8513-5bb901527f41/service/ce549504-cde6-4d20-a142-01dc10f54b5f/deployments
echo.
echo You should see a new deployment with message:
echo "Test auto-deploy after webhook reconnection"
echo.
pause
