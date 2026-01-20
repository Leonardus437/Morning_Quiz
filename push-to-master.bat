@echo off
cd /d "d:\Morning_Quiz-master"
echo Pushing main branch to master for Cloudflare...
"C:\Program Files\Git\bin\git.exe" push origin main:master -f
echo.
echo Done! Check Cloudflare in 2 minutes.
pause
