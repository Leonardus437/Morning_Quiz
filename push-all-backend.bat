@echo off
cd /d "f:\SIDE HUSTLE\Morning_Quiz"

echo Adding ALL backend Python files...
git add -f backend/*.py

echo Committing...
git commit -m "Add all missing backend Python modules"

echo Pushing to GitHub...
git push origin master

echo.
echo Done! Now redeploy on Render.
pause
