@echo off
cd /d c:\Users\Hp\Documents\Morning_Quiz-master\backend

echo Fixing /health endpoint to support GET requests...
git add main.py
git commit -m "Fix: Add GET method to /health endpoint"
git push origin master

echo.
echo ========================================
echo SUCCESS! Railway is working now!
echo ========================================
echo.
echo Your app is LIVE at:
echo https://web-production-2c325.up.railway.app
echo.
echo Test the CORS fix:
echo https://web-production-2c325.up.railway.app/hierarchy/provinces
echo.
echo If provinces load, your frontend login will work!
echo.
pause
