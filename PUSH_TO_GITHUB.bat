@echo off
echo ========================================
echo  TVET Quiz - Push to GitHub
echo ========================================
echo.

REM Check if git is initialized
if not exist .git (
    echo Initializing Git repository...
    git init
    echo.
)

REM Check if remote exists
git remote -v | findstr origin >nul
if errorlevel 1 (
    echo.
    echo Please enter your GitHub repository URL:
    echo Example: https://github.com/YOUR_USERNAME/tvet-quiz-system.git
    set /p REPO_URL="Repository URL: "
    git remote add origin %REPO_URL%
    echo.
)

echo Adding all files...
git add .
echo.

echo Enter commit message (or press Enter for default):
set /p COMMIT_MSG="Commit message: "
if "%COMMIT_MSG%"=="" set COMMIT_MSG=Update TVET Quiz System

echo.
echo Committing changes...
git commit -m "%COMMIT_MSG%"
echo.

echo Pushing to GitHub...
git branch -M main
git push -u origin main

echo.
echo ========================================
echo  Push Complete!
echo ========================================
echo.
echo Your code is now on GitHub.
echo Next steps:
echo 1. Go to Cloudflare Pages dashboard
echo 2. Connect your GitHub repository
echo 3. Deploy to tsskwizi.pages.dev
echo.
echo See GITHUB_CLOUDFLARE_DEPLOYMENT.md for details
echo.
pause
