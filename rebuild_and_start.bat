@echo off
echo ========================================
echo Morning Quiz System - Full Rebuild
echo ========================================
echo.

echo [1/4] Stopping containers...
docker-compose down

echo.
echo [2/4] Rebuilding frontend (this takes 2-3 minutes)...
docker-compose build --no-cache frontend

echo.
echo [3/4] Starting all services...
docker-compose up -d

echo.
echo [4/4] Waiting for services to be ready...
timeout /t 10 /nobreak

echo.
echo ========================================
echo System Ready!
echo ========================================
echo.
echo Admin Panel: http://localhost:3000/admin
echo Username: admin
echo Password: admin123
echo.
echo Network Access: http://192.168.183.61:3000/admin
echo.
echo Press any key to open admin panel...
pause > nul
start http://localhost:3000/admin
