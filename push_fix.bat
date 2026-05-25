@echo off
cd /d c:\Users\Hp\Documents\Morning_Quiz-master\backend

echo Committing nixpacks fix...
git add nixpacks.toml
git commit -m "Fix: Update nixpacks to Python 3.11 for Railway deployment"

echo Pushing to master branch...
git push origin master

echo.
echo === IMPORTANT ===
echo Your code is on MASTER branch
echo Railway should auto-deploy now!
echo.
echo If still not deploying, go to Railway Settings and verify:
echo Branch: master (not main)
echo.
pause
