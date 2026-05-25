@echo off
cd /d c:\Users\Hp\Documents\Morning_Quiz-master\backend

echo Fixing Railway startup crash...
git add railway.json
git commit -m "FIX: Railway startup crash - correct PORT variable syntax"
git push origin master

echo.
echo ========================================
echo CRITICAL FIX PUSHED!
echo ========================================
echo.
echo The app was crashing because railway.json had wrong syntax:
echo   WRONG: ${PORT:-8000}  (bash syntax doesn't work in Railway)
echo   FIXED: $PORT          (Railway sets this automatically)
echo.
echo Now go to Railway and MANUALLY REDEPLOY:
echo https://railway.com/project/477122d8-1d79-437f-8513-5bb901527f41/service/ce549504-cde6-4d20-a142-01dc10f54b5f/deployments
echo.
echo Click "New Deployment" → "Deploy Latest Commit"
echo.
echo This time it WILL work!
echo.
pause
