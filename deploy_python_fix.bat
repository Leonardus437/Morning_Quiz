@echo off
cd /d c:\Users\Hp\Documents\Morning_Quiz-master\backend

echo ========================================
echo FIXING PORT VARIABLE ISSUE
echo ========================================
echo.
echo Problem: Railway not expanding $PORT in Dockerfile CMD
echo.
echo Solution: Created start.py Python script that:
echo   1. Reads PORT from os.getenv("PORT", "8000")
echo   2. Starts uvicorn with correct port
echo.

git add start.py Dockerfile
git commit -m "FIX: Use Python script to read PORT environment variable"
git push origin master

echo.
echo ========================================
echo PUSHED! NOW DEPLOY IN RAILWAY:
echo ========================================
echo.
echo 1. Go to: https://railway.com/project/477122d8-1d79-437f-8513-5bb901527f41/service/ce549504-cde6-4d20-a142-01dc10f54b5f/deployments
echo.
echo 2. Click "New Deployment" -^> "Deploy Latest Commit"
echo.
echo 3. This WILL work because Python reads environment variables correctly!
echo.
pause
