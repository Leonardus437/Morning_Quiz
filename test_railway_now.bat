@echo off
cd /d c:\Users\Hp\Documents\Morning_Quiz-master\backend

echo Making visible change to trigger Railway deployment...
echo.

git add .
git commit -m "FORCE DEPLOY: Trigger Railway rebuild - %date% %time%"
git push origin master

echo.
echo ========================================
echo CODE PUSHED TO GITHUB!
echo ========================================
echo.
echo Now check Railway Deployments:
echo https://railway.com/project/477122d8-1d79-437f-8513-5bb901527f41/service/ce549504-cde6-4d20-a142-01dc10f54b5f/deployments
echo.
echo Wait 60 seconds and refresh the page.
echo.
echo If you see a NEW deployment starting = WEBHOOK FIXED!
echo If NOTHING happens = Webhook still dead, need Option 1 or 2
echo.
pause
