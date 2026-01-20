@echo off
cd /d d:\Morning_Quiz-master

echo Adding fixed backend...
"C:\Program Files\Git\bin\git.exe" add backend/main.py

echo Committing...
"C:\Program Files\Git\bin\git.exe" commit -m "Fix backend syntax errors and add anti-cheating endpoint"

echo.
set /p TOKEN="Paste GitHub token: "

echo.
echo Pushing to GitHub...
"C:\Program Files\Git\bin\git.exe" push https://%TOKEN%@github.com/Leonardus437/Morning_Quiz.git main

echo.
echo ========================================
echo   Backend Fixed and Deployed!
echo ========================================
echo.
echo Monitor Render: https://dashboard.render.com/
echo Backend will restart automatically in 2-3 minutes
echo.
echo Test: https://tvet-quiz-backend.onrender.com/health
echo.
pause
