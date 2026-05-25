@echo off
cd /d c:\Users\Hp\Documents\Morning_Quiz-master\backend

echo ========================================
echo SWITCHING TO NIXPACKS BUILDER
echo ========================================
echo.
echo Problem: Dockerfile builds are cached, Railway keeps using old image
echo.
echo Solution: Switch to NIXPACKS builder
echo   - Forces complete rebuild
echo   - Uses start.py to handle PORT correctly
echo.

git add railway.json
git commit -m "CRITICAL: Switch to Nixpacks builder to force rebuild"
git push origin master

echo.
echo ========================================
echo PUSHED! NOW DEPLOY:
echo ========================================
echo.
echo 1. Go to Railway Deployments
echo.
echo 2. Click "New Deployment" -^> "Deploy Latest Commit"
echo.
echo 3. Railway will use NIXPACKS (not Dockerfile)
echo.
echo 4. Watch Build Logs - should see "Using Nixpacks"
echo.
echo 5. This WILL work!
echo.
pause
