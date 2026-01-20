@echo off
cd /d d:\Morning_Quiz-master

echo Removing old git...
rd /s /q .git 2>nul

echo Initializing repository...
"C:\Program Files\Git\bin\git.exe" init
"C:\Program Files\Git\bin\git.exe" config user.email "leonardus437@gmail.com"
"C:\Program Files\Git\bin\git.exe" config user.name "Leonardus437"

echo.
set /p TOKEN="Paste GitHub token: "

echo.
echo Adding remote...
"C:\Program Files\Git\bin\git.exe" remote add origin https://%TOKEN%@github.com/Leonardus437/Morning_Quiz.git

echo.
echo Adding files...
"C:\Program Files\Git\bin\git.exe" add .

echo.
echo Committing...
"C:\Program Files\Git\bin\git.exe" commit -m "Add anti-cheating system"

echo.
echo Renaming branch to main...
"C:\Program Files\Git\bin\git.exe" branch -M main

echo.
echo Pushing...
"C:\Program Files\Git\bin\git.exe" push -u origin main --force

echo.
echo ========================================
echo   DEPLOYED!
echo ========================================
echo.
echo Cloudflare: https://dash.cloudflare.com/86089f0bb941af81d975a82b892fe038/pages/view/tsskwizi
echo Test: https://tsskwizi.pages.dev
echo.
pause
