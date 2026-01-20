@echo off
echo ========================================
echo DEPLOYING FIXED BACKEND TO PRODUCTION
echo ========================================
echo.

cd /d "d:\Morning_Quiz-master"

echo [1/3] Adding fixed files...
"C:\Program Files\Git\bin\git.exe" add backend/main.py backend/ai_grader.py
if errorlevel 1 (
    echo ERROR: Failed to add files
    pause
    exit /b 1
)

echo [2/3] Committing changes...
"C:\Program Files\Git\bin\git.exe" commit -m "Fix: Remove all merge conflicts from backend files"
if errorlevel 1 (
    echo ERROR: Failed to commit
    pause
    exit /b 1
)

echo [3/3] Pushing to GitHub...
"C:\Program Files\Git\bin\git.exe" push origin main
if errorlevel 1 (
    echo ERROR: Failed to push - check your GitHub token
    pause
    exit /b 1
)

echo.
echo ========================================
echo SUCCESS! Backend deployed to GitHub
echo ========================================
echo.
echo Render will auto-deploy in 1-2 minutes
echo Check: https://dashboard.render.com/
echo.
pause
