@echo off
cd /d c:\Users\Hp\Documents\Morning_Quiz-master\backend

echo ========================================
echo FIXING RAILWAY DOCKERFILE
echo ========================================
echo.
echo Problem: Dockerfile CMD used exec form ["sh", "-c", "..."]
echo          which doesn't expand PORT variable correctly
echo.
echo Solution: Changed to shell form (no brackets)
echo          CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
echo.

git add Dockerfile
git commit -m "FIX: Dockerfile CMD syntax for Railway PORT variable"
git push origin master

echo.
echo ========================================
echo PUSHED TO GITHUB!
echo ========================================
echo.
echo Now go to Railway and MANUALLY TRIGGER DEPLOY:
echo.
echo 1. https://railway.com/project/477122d8-1d79-437f-8513-5bb901527f41/service/ce549504-cde6-4d20-a142-01dc10f54b5f/deployments
echo.
echo 2. Click "New Deployment" button (top right)
echo.
echo 3. Click "Deploy Latest Commit"
echo.
echo 4. Watch Deploy Logs - should see:
echo    "INFO: Uvicorn running on http://0.0.0.0:XXXX"
echo.
echo 5. If successful, test:
echo    https://web-production-2c325.up.railway.app/health
echo.
pause
