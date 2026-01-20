@echo off
cd /d d:\Morning_Quiz-master

echo Removing git history to clear secrets...
rd /s /q .git 2>nul

echo Initializing fresh repository...
"C:\Program Files\Git\bin\git.exe" init
"C:\Program Files\Git\bin\git.exe" config user.email "leonardus437@gmail.com"
"C:\Program Files\Git\bin\git.exe" config user.name "Leonardus437"

echo.
set /p TOKEN="Paste your GitHub token: "

echo.
echo Adding remote...
"C:\Program Files\Git\bin\git.exe" remote add origin https://%TOKEN%@github.com/Leonardus437/Morning_Quiz.git

echo.
echo Adding files...
"C:\Program Files\Git\bin\git.exe" add .

echo.
echo Committing...
"C:\Program Files\Git\bin\git.exe" commit -m "Add anti-cheating system - production ready"

echo.
echo Pushing to GitHub...
"C:\Program Files\Git\bin\git.exe" push -u origin main --force

echo.
echo ========================================
echo   SUCCESS! Deployment Complete!
echo ========================================
echo.
echo Monitor:
echo - Frontend: https://dash.cloudflare.com/86089f0bb941af81d975a82b892fe038/pages/view/tsskwizi
echo - Backend: https://dashboard.render.com/
echo.
echo Test: https://tsskwizi.pages.dev
echo.
pause
