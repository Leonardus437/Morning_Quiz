@echo off
echo Fixing merge conflicts in backend/main.py...

cd /d d:\Morning_Quiz-master\backend

echo Removing conflict markers...
powershell -Command "(Get-Content main.py) -replace '<<<<<<< HEAD', '' -replace '=======', '' -replace '>>>>>>> .*', '' | Set-Content main.py.tmp"
move /Y main.py.tmp main.py

cd ..

echo.
echo Committing fix...
"C:\Program Files\Git\bin\git.exe" add backend/main.py
"C:\Program Files\Git\bin\git.exe" commit -m "Fix merge conflicts in main.py"

echo.
set /p TOKEN="Paste GitHub token: "

echo.
echo Pushing fix...
"C:\Program Files\Git\bin\git.exe" push https://%TOKEN%@github.com/Leonardus437/Morning_Quiz.git main

echo.
echo ========================================
echo   Fix deployed! Backend will restart.
echo ========================================
echo.
echo Monitor: https://dashboard.render.com/
echo.
pause
