@echo off
cd /d d:\Morning_Quiz-master

echo Initializing git repository...
"C:\Program Files\Git\bin\git.exe" init

echo Adding remote...
"C:\Program Files\Git\bin\git.exe" remote add origin https://github.com/Leonardus437/Morning_Quiz.git

echo Adding files...
"C:\Program Files\Git\bin\git.exe" add .

echo Committing...
"C:\Program Files\Git\bin\git.exe" commit -m "Add comprehensive anti-cheating system with fullscreen lock, tab/window detection, copy/paste prevention, three-strike warnings, auto-submit, and teacher notifications"

echo Pushing to GitHub...
"C:\Program Files\Git\bin\git.exe" push -u origin main

echo.
echo Deployment complete!
echo Monitor: https://dash.cloudflare.com/86089f0bb941af81d975a82b892fe038/pages/view/tsskwizi
echo Test: https://tsskwizi.pages.dev
pause
