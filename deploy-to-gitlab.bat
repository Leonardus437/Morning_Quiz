@echo off
cd /d "d:\Morning_Quiz-master"
echo ========================================
echo DEPLOYING TO GITLAB
echo ========================================
echo.
echo [1/4] Adding GitLab remote...
"C:\Program Files\Git\bin\git.exe" remote add gitlab https://gitlab.com/leotuyi10/tsskwizi.git
if errorlevel 1 (
    echo GitLab remote already exists, updating...
    "C:\Program Files\Git\bin\git.exe" remote set-url gitlab https://gitlab.com/leotuyi10/tsskwizi.git
)
echo [2/4] Adding all files...
"C:\Program Files\Git\bin\git.exe" add .
echo [3/4] Committing...
"C:\Program Files\Git\bin\git.exe" commit -m "Deploy anti-cheating system to production"
if errorlevel 1 (
    echo No new changes, continuing...
)
echo [4/4] Pushing to GitLab...
"C:\Program Files\Git\bin\git.exe" push gitlab main:master -f
echo.
echo ========================================
echo SUCCESS! Pushed to GitLab
echo ========================================
echo.
echo GitLab will auto-deploy to Cloudflare Pages
echo Check: https://gitlab.com/leotuyi10/tsskwizi
echo Cloudflare: https://dash.cloudflare.com/86089f0bb941af81d975a82b892fe038/pages/view/tsskwizi
echo.
pause
