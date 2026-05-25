@echo off
cd /d c:\Users\Hp\Documents\Morning_Quiz-master\backend

echo Removing conflicting nixpacks.toml...
git rm nixpacks.toml
git commit -m "Remove nixpacks.toml - use Dockerfile only for Railway"
git push origin master

echo.
echo Done! Now Railway will use Dockerfile.
echo.
echo NEXT STEPS:
echo 1. Go to Railway Settings
echo 2. Scroll to "Builder" section
echo 3. Verify it shows "Dockerfile" (not Nixpacks)
echo 4. Click "New Deployment" to trigger deploy
echo.
pause
