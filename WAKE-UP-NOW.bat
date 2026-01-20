@echo off
echo EMERGENCY FIX - ERR_EMPTY_RESPONSE
echo ===================================
echo.

cd /d "f:\SIDE HUSTLE\Morning_Quiz"

echo [1] Stopping all containers...
docker-compose down

echo.
echo [2] Checking frontend Dockerfile...
if exist "frontend\Dockerfile" (
    echo ✓ Frontend Dockerfile exists
) else (
    echo ✗ Frontend Dockerfile missing!
    pause
    exit /b 1
)

echo.
echo [3] Rebuilding frontend container from scratch...
docker-compose build --no-cache frontend

echo.
echo [4] Starting all services...
docker-compose up -d

echo.
echo [5] Waiting for services to initialize...
timeout /t 15 /nobreak >nul

echo.
echo [6] Checking container status...
docker-compose ps

echo.
echo [7] Checking frontend logs...
docker-compose logs frontend --tail=5

echo.
echo [8] Testing connection...
for /l %%i in (1,1,3) do (
    echo Attempt %%i/3...
    curl -s -I http://localhost:3000 | find "200 OK" >nul 2>&1
    if !errorLevel! == 0 (
        echo ✓ Frontend responding!
        goto :success
    )
    timeout /t 5 /nobreak >nul
)

echo.
echo [9] ALTERNATIVE: Try direct container access...
echo If localhost:3000 still fails, try:
echo - http://127.0.0.1:3000
echo - Check Windows Firewall
echo - Try different browser

echo.
echo [10] Manual container restart if needed...
docker-compose restart frontend

:success
echo.
echo Press any key to continue . . .
pause >nul