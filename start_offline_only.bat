@echo off
echo ================================================
echo STARTING OFFLINE-ONLY QUIZ SYSTEM
echo ================================================
echo.

echo Disabling Windows network adapters for true offline test...
netsh interface set interface "Wi-Fi" admin=disable >nul 2>&1
netsh interface set interface "Ethernet" admin=disable >nul 2>&1

echo Starting Docker containers...
docker-compose -f docker-compose.offline.yml up -d

echo.
echo Waiting for services to start...
timeout /t 10 /nobreak >nul

echo.
echo Re-enabling network adapters...
netsh interface set interface "Wi-Fi" admin=enable >nul 2>&1
netsh interface set interface "Ethernet" admin=enable >nul 2>&1

echo.
echo ================================================
echo OFFLINE SYSTEM READY!
echo ================================================
echo.
echo Access URLs (LAN only - no internet needed):
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr "IPv4" ^| findstr "192.168"') do (
    set IP=%%a
    set IP=!IP: =!
    echo   http://!IP!:3000
)
echo.
echo Default Login: admin / admin123
echo.
pause