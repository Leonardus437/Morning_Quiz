@echo off
cd /d d:\Morning_Quiz-master

echo ========================================
echo   GitHub Personal Access Token Setup
echo ========================================
echo.
echo You need a GitHub Personal Access Token to push code.
echo.
echo To generate one:
echo 1. Go to: https://github.com/settings/tokens/new
echo 2. Note: "Deploy TVET Quiz"
echo 3. Select scope: repo (full control)
echo 4. Click "Generate token"
echo 5. Copy the token (starts with ghp_)
echo.
echo ========================================
echo.

set /p TOKEN="Paste your GitHub token here: "

echo.
echo Setting up remote with token...
"C:\Program Files\Git\bin\git.exe" remote remove origin 2>nul
"C:\Program Files\Git\bin\git.exe" remote add origin https://%TOKEN%@github.com/Leonardus437/Morning_Quiz.git

echo.
echo Creating main branch...
"C:\Program Files\Git\bin\git.exe" checkout -b main 2>nul

echo.
echo Adding files...
"C:\Program Files\Git\bin\git.exe" add .

echo.
echo Committing...
"C:\Program Files\Git\bin\git.exe" commit -m "Add comprehensive anti-cheating system with fullscreen lock, tab/window detection, copy/paste prevention, three-strike warnings, auto-submit, and teacher notifications"

echo.
echo Pushing to GitHub...
"C:\Program Files\Git\bin\git.exe" push -u origin main --force

echo.
echo ========================================
echo   Deployment Complete!
echo ========================================
echo.
echo Monitor deployments:
echo Frontend: https://dash.cloudflare.com/86089f0bb941af81d975a82b892fe038/pages/view/tsskwizi
echo Backend: https://dashboard.render.com/
echo.
echo Test site: https://tsskwizi.pages.dev
echo.
pause
