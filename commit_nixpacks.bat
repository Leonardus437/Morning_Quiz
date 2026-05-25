@echo off
cd /d c:\Users\Hp\Documents\Morning_Quiz-master\backend

echo Committing railway.json (Nixpacks config)...
git add railway.json
git commit -m "CRITICAL: Switch to Nixpacks builder - force complete rebuild"
git push origin master

echo.
echo ========================================
echo PUSHED NIXPACKS CONFIG!
echo ========================================
echo.
echo Railway will now use NIXPACKS instead of Dockerfile
echo This forces a complete rebuild (no cache)
echo.
echo NOW DEPLOY IN RAILWAY:
echo 1. Go to: https://railway.com/project/477122d8-1d79-437f-8513-5bb901527f41/service/ce549504-cde6-4d20-a142-01dc10f54b5f/deployments
echo.
echo 2. Click "New Deployment" -^> "Deploy Latest Commit"
echo.
echo 3. Watch BUILD LOGS - should see "Using Nixpacks"
echo.
echo 4. Watch DEPLOY LOGS - should see "INFO: Uvicorn running"
echo.
pause
