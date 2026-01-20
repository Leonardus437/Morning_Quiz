@echo off
echo FIXING FRONTEND HEALTH ISSUE
echo ==============================
echo.

cd /d "f:\SIDE HUSTLE\Morning_Quiz"

echo [1] Checking frontend logs for health issue...
docker-compose logs frontend --tail=50

echo.
echo [2] Restarting just the frontend...
docker-compose restart frontend

echo.
echo [3] Waiting for frontend to be healthy...
timeout /t 20 /nobreak >nul

echo.
echo [4] Checking status...
docker-compose ps

echo.
echo [5] Testing URLs...
echo Testing http://localhost:3000
start http://localhost:3000

echo.
echo [6] If browser opened, try these:
echo - Student: http://localhost:3000
echo - Teacher: http://localhost:3000/teacher
echo - Admin: http://localhost:3000/admin

pause