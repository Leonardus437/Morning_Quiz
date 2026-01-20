@echo off
cd /d d:\Morning_Quiz-master

echo Configuring git...
"C:\Program Files\Git\bin\git.exe" config user.email "leonardus437@gmail.com"
"C:\Program Files\Git\bin\git.exe" config user.name "Leonardus437"

echo Checking repository status...
"C:\Program Files\Git\bin\git.exe" remote -v

echo Adding files...
"C:\Program Files\Git\bin\git.exe" add .

echo Committing...
"C:\Program Files\Git\bin\git.exe" commit -m "Add comprehensive anti-cheating system with fullscreen lock, tab/window detection, copy/paste prevention, three-strike warnings, auto-submit, and teacher notifications"

echo Pushing to GitHub...
"C:\Program Files\Git\bin\git.exe" push origin main

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
