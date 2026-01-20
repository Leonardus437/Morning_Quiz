@echo off
cd /d d:\Morning_Quiz-master

echo Checking current git remote...
"C:\Program Files\Git\bin\git.exe" remote -v

echo.
echo Removing old remotes...
"C:\Program Files\Git\bin\git.exe" remote remove origin 2>nul

echo.
echo Adding GitHub remote...
"C:\Program Files\Git\bin\git.exe" remote add origin https://github.com/Leonardus437/Morning_Quiz.git

echo.
echo Verifying remote...
"C:\Program Files\Git\bin\git.exe" remote -v

echo.
echo Checking current branch...
"C:\Program Files\Git\bin\git.exe" branch

echo.
echo Creating main branch if needed...
"C:\Program Files\Git\bin\git.exe" checkout -b main 2>nul

echo.
echo Pulling from GitHub (if exists)...
"C:\Program Files\Git\bin\git.exe" pull origin main --allow-unrelated-histories 2>nul

echo.
echo Adding all files...
"C:\Program Files\Git\bin\git.exe" add .

echo.
echo Committing changes...
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
