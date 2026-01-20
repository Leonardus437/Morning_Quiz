@echo off
echo ========================================
echo   FIX NULL BYTES AND PUSH TO GITHUB
echo ========================================
echo.

echo This will fix corrupted Python files and push to GitHub
pause

echo.
echo [1/6] Finding and removing null bytes from Python files...
cd backend

for %%f in (*.py) do (
    echo Checking %%f...
    type "%%f" | find /v "" > "%%f.tmp" 2>nul
    if exist "%%f.tmp" (
        move /y "%%f.tmp" "%%f" >nul
        echo   Fixed: %%f
    )
)

cd ..

echo.
echo [2/6] Removing unnecessary files from git...
git rm --cached backend/test_*.py backend/check_*.py backend/debug_*.py backend/verify_*.py backend/*_test.py 2>nul

echo.
echo [3/6] Adding clean files...
git add backend/main.py
git add backend/requirements.txt
git add backend/Dockerfile
git add backend/init_db.py
git add .gitignore
git add render.yaml

echo.
echo [4/6] Committing changes...
git commit -m "Fix: Remove null bytes from Python files for Render deployment"

echo.
echo [5/6] Pushing to GitHub...
git push origin master

echo.
echo [6/6] Done! Now redeploy in Render...
echo.
echo ========================================
echo   SUCCESS! Files cleaned and pushed
echo ========================================
echo.
echo NEXT STEPS IN RENDER:
echo 1. Go to your service dashboard
echo 2. Click "Manual Deploy" 
echo 3. Select "Clear build cache & deploy"
echo.
pause
