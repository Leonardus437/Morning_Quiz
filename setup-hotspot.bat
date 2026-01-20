@echo off
echo ========================================
echo   TVET Quiz - Hotspot Setup
echo ========================================
echo.

REM Check admin rights
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: Please run as Administrator!
    echo Right-click this file and select "Run as administrator"
    pause
    exit /b 1
)

echo [1/4] Stopping existing hotspot...
netsh wlan stop hostednetwork >nul 2>&1

echo [2/4] Creating new hotspot...
echo      Network Name: TVETQuiz
echo      Password: quiz12345
netsh wlan set hostednetwork mode=allow ssid=TVETQuiz key=quiz12345

echo [3/4] Starting hotspot...
netsh wlan start hostednetwork

if %errorLevel% equ 0 (
    echo.
    echo ========================================
    echo   SUCCESS! Hotspot is running
    echo ========================================
    echo.
    echo HOTSPOT DETAILS:
    echo   Network Name: TVETQuiz
    echo   Password: quiz12345
    echo.
    echo STUDENT ACCESS:
    echo   1. Connect to WiFi: TVETQuiz
    echo   2. Open browser
    echo   3. Go to: http://192.168.137.1:3000
    echo.
    echo [4/4] Finding your hotspot IP...
    ipconfig | findstr /C:"Wireless LAN adapter Local Area Connection"
    ipconfig | findstr /C:"IPv4"
    echo.
    echo ========================================
    echo Share this URL with students:
    echo http://192.168.137.1:3000
    echo ========================================
    echo.
    echo Press any key to start Docker containers...
    pause >nul
    
    cd /d "%~dp0"
    docker-compose up -d
    
    echo.
    echo ========================================
    echo System is ready!
    echo ========================================
    echo.
    echo To stop hotspot later, run: stop-hotspot.bat
    echo.
) else (
    echo.
    echo ERROR: Could not start hotspot!
    echo.
    echo POSSIBLE REASONS:
    echo 1. Your WiFi adapter doesn't support hotspot
    echo 2. WiFi is disabled
    echo 3. Another hotspot is running
    echo.
    echo SOLUTION: Use your phone hotspot instead
    echo.
)

pause
