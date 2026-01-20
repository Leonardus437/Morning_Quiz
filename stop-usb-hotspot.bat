@echo off
echo ========================================
echo   Stopping USB WiFi Hotspot
echo ========================================
echo.

REM Check admin rights
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: Please run as Administrator!
    pause
    exit /b 1
)

echo Stopping hotspot...
netsh wlan stop hostednetwork

echo Stopping Docker containers...
cd /d "%~dp0"
docker-compose down

echo.
echo ========================================
echo   System stopped successfully
echo ========================================
echo.
pause
