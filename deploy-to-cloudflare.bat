@echo off
cd /d "d:\Morning_Quiz-master"
echo ========================================
echo PUSHING TO MASTER BRANCH FOR CLOUDFLARE
echo ========================================
echo.
echo [1/4] Adding frontend files...
"C:\Program Files\Git\bin\git.exe" add frontend/
"C:\Program Files\Git\bin\git.exe" add backend/
"C:\Program Files\Git\bin\git.exe" add .gitignore
echo [2/4] Committing...
"C:\Program Files\Git\bin\git.exe" commit -m "Deploy anti-cheating system to production"
if errorlevel 1 (
    echo No new changes, continuing...
)
echo [3/4] Pushing to main...
"C:\Program Files\Git\bin\git.exe" push origin main
echo [4/4] Pushing to master for Cloudflare...
"C:\Program Files\Git\bin\git.exe" push origin main:master -f
echo.
echo ========================================
echo SUCCESS! Cloudflare will auto-deploy now
echo ========================================
echo.
echo Monitor: https://dash.cloudflare.com/86089f0bb941af81d975a82b892fe038/pages/view/tsskwizi
echo Wait 2-3 minutes for build to complete
echo.
pause
