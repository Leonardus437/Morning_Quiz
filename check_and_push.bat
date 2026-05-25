@echo off
echo Checking Git status...
cd /d c:\Users\Hp\Documents\Morning_Quiz-master\backend

echo.
echo === Current Branch ===
git branch

echo.
echo === Last 3 Local Commits ===
git log --oneline -3

echo.
echo === Checking Remote Status ===
git fetch origin
git status

echo.
echo === Pushing to GitHub ===
git push origin master --force

echo.
echo Done! Check Railway in 2 minutes: https://railway.com/project/477122d8-1d79-437f-8513-5bb901527f41/service/ce549504-cde6-4d20-a142-01dc10f54b5f/deployments
pause
