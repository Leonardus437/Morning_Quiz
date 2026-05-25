@echo off
cd /d c:\Users\Hp\Documents\Morning_Quiz-master\backend

echo Checking git status...
git status

echo.
echo Checking if start.py is tracked...
git ls-files | findstr start.py

echo.
echo Adding start.py explicitly...
git add -f start.py
git add Dockerfile

echo.
echo Committing...
git commit -m "FORCE: Add start.py and updated Dockerfile"

echo.
echo Pushing...
git push origin master

echo.
echo Done! Now deploy in Railway.
pause
