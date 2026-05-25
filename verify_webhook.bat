@echo off
cd /d c:\Users\Hp\Documents\Morning_Quiz-master\backend

echo Testing Railway auto-deploy...
echo.

git commit --allow-empty -m "Test: Verify Railway webhook after reconnection"
git push origin master

echo.
echo ========================================
echo Test commit pushed to GitHub!
echo ========================================
echo.
echo Now check Railway Deployments page:
echo https://railway.com/project/477122d8-1d79-437f-8513-5bb901527f41/service/ce549504-cde6-4d20-a142-01dc10f54b5f/deployments
echo.
echo Within 30-60 seconds you should see:
echo - New deployment starting
echo - Commit message: "Test: Verify Railway webhook after reconnection"
echo.
echo If you see the deployment = WEBHOOK FIXED!
echo If nothing happens = Webhook still broken
echo.
pause
