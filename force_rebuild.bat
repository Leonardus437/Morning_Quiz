@echo off
cd /d c:\Users\Hp\Documents\Morning_Quiz-master\backend

echo Forcing Railway to rebuild by updating requirements.txt...
git add requirements.txt
git commit -m "Force Railway rebuild - update requirements.txt"
git push origin master

echo.
echo ========================================
echo PUSHED! Now do this IMMEDIATELY:
echo ========================================
echo.
echo 1. Go to Railway: https://railway.com/project/477122d8-1d79-437f-8513-5bb901527f41/service/ce549504-cde6-4d20-a142-01dc10f54b5f/settings
echo.
echo 2. Scroll to "Deploy" section
echo.
echo 3. Find "Custom Start Command" 
echo.
echo 4. Click in the text box (even if it already has a command)
echo.
echo 5. Press SPACE then BACKSPACE (to trigger a change)
echo.
echo 6. Click "Save" or press Enter
echo.
echo This will force Railway to redeploy!
echo.
pause
