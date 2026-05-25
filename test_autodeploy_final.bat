@echo off
cd /d c:\Users\Hp\Documents\Morning_Quiz-master\backend

echo ========================================
echo TESTING RAILWAY AUTO-DEPLOY
echo ========================================
echo.
echo Pushing health endpoint fix to test if webhook works...
git add main.py
git commit -m "Test: Verify Railway auto-deploy webhook"
git push origin master

echo.
echo ========================================
echo PUSHED TO GITHUB!
echo ========================================
echo.
echo Now check Railway Deployments in 60 seconds:
echo https://railway.com/project/477122d8-1d79-437f-8513-5bb901527f41/service/ce549504-cde6-4d20-a142-01dc10f54b5f/deployments
echo.
echo If you see a NEW deployment starting automatically = WEBHOOK FIXED!
echo If nothing happens = Webhook still broken (but manual deploy works)
echo.
echo After deployment completes, test:
echo https://web-production-2c325.up.railway.app/health
echo.
echo Should return JSON (not "Method Not Allowed")
echo.
pause
