@echo off
color 0B
echo.
echo ========================================
echo   GIT-BASED DEPLOYMENT (ALTERNATIVE)
echo ========================================
echo.
echo This method pushes to GitHub, which triggers
echo Cloudflare Pages automatic deployment
echo.
echo ========================================
echo.

echo [1/5] Checking git status...
git status
if %errorlevel% neq 0 (
    color 0C
    echo.
    echo ERROR: Not a git repository or git not installed
    echo.
    pause
    exit /b 1
)

echo.
echo [2/5] Adding all changes...
git add .

echo.
echo [3/5] Committing changes...
git commit -m "Fix: Token expiration and restore My Questions button"
if %errorlevel% neq 0 (
    echo No changes to commit or commit failed
)

echo.
echo [4/5] Pushing to GitHub...
git push origin main
if %errorlevel% neq 0 (
    color 0C
    echo.
    echo ERROR: Git push failed
    echo.
    echo Possible reasons:
    echo  1. Not authenticated with GitHub
    echo  2. No remote repository configured
    echo  3. Network connection issue
    echo.
    echo Try: git remote -v
    echo.
    pause
    exit /b 1
)

echo.
color 0A
echo ========================================
echo   GIT PUSH SUCCESSFUL!
echo ========================================
echo.
echo Cloudflare Pages will automatically deploy from GitHub
echo.
echo Check deployment status:
echo  1. Go to: https://dash.cloudflare.com/
echo  2. Select: Pages
echo  3. Select: tsskwizi project
echo  4. View: Latest deployment
echo.
echo Deployment usually takes 2-5 minutes
echo.
echo ========================================
echo.
pause
