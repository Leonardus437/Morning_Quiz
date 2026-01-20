@echo off
echo ========================================
echo   CLEAN DEPLOYMENT PREPARATION
echo ========================================
echo.

echo This will:
echo 1. Create a new clean branch for deployment
echo 2. Remove corrupted files
echo 3. Keep only essential files
echo 4. Push to GitHub
echo.
pause

echo.
echo [1/5] Creating deployment branch...
git checkout -b render-deploy

echo.
echo [2/5] Removing test and debug files...
git rm -r --cached backend/test_*.py backend/check_*.py backend/debug_*.py backend/verify_*.py 2>nul

echo.
echo [3/5] Adding .gitignore...
git add .gitignore

echo.
echo [4/5] Committing clean version...
git add backend/main.py backend/requirements.txt backend/Dockerfile
git add frontend/
git add docker-compose.yml
git add render.yaml
git commit -m "Clean deployment version for Render"

echo.
echo [5/5] Pushing to GitHub...
git push origin render-deploy

echo.
echo ========================================
echo   DONE! Now deploy from render-deploy branch
echo ========================================
echo.
echo In Render:
echo 1. Go to your service settings
echo 2. Change Branch to: render-deploy
echo 3. Click "Manual Deploy"
echo.
pause
