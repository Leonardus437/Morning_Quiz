@echo off
echo ========================================
echo   USB WiFi Adapter Hotspot Setup
echo   Supports 30-50+ Devices
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

echo [Step 1/5] Checking USB WiFi adapter...
echo.

REM List all WiFi adapters
netsh wlan show drivers

echo.
echo ========================================
echo IMPORTANT: Check above output
echo ========================================
echo.
echo Look for your USB WiFi adapter and check:
echo   "Hosted network supported: Yes"
echo.
echo If you see "Yes" for USB adapter, continue!
echo If you see "No", your adapter doesn't support AP mode.
echo.
pause

echo.
echo [Step 2/5] Stopping any existing hotspot...
netsh wlan stop hostednetwork >nul 2>&1

echo [Step 3/5] Creating new hotspot on USB adapter...
echo.
echo   Network Name: TVETQuiz
echo   Password: quiz12345
echo   Capacity: 30-50 devices
echo.

netsh wlan set hostednetwork mode=allow ssid=TVETQuiz key=quiz12345

echo.
echo [Step 4/5] Starting hotspot...
netsh wlan start hostednetwork

if %errorLevel% equ 0 (
    echo.
    echo ========================================
    echo   SUCCESS! USB Hotspot is Running
    echo ========================================
    echo.
    echo HOTSPOT DETAILS:
    echo   Network Name: TVETQuiz
    echo   Password: quiz12345
    echo   Capacity: 30-50 devices (USB adapter)
    echo.
    echo [Step 5/5] Finding your IP address...
    echo.
    ipconfig | findstr /C:"Wireless LAN adapter Local Area Connection" /C:"IPv4"
    echo.
    echo ========================================
    echo STUDENT ACCESS URL:
    echo http://192.168.137.1:3000
    echo ========================================
    echo.
    echo INSTRUCTIONS FOR STUDENTS:
    echo 1. Connect to WiFi: TVETQuiz
    echo 2. Password: quiz12345
    echo 3. Open browser
    echo 4. Go to: http://192.168.137.1:3000
    echo.
    echo ========================================
    echo   Ready for 60+ Students!
    echo ========================================
    echo.
    echo Starting Docker containers...
    cd /d "%~dp0"
    docker-compose up -d
    
    echo.
    echo ========================================
    echo   System is READY!
    echo ========================================
    echo.
    echo Share with students:
    echo   WiFi: TVETQuiz
    echo   Password: quiz12345
    echo   URL: http://192.168.137.1:3000
    echo.
    echo To stop: Run stop-usb-hotspot.bat
    echo.
) else (
    echo.
    echo ========================================
    echo   ERROR: Could not start hotspot
    echo ========================================
    echo.
    echo TROUBLESHOOTING:
    echo.
    echo 1. Make sure USB WiFi adapter is plugged in
    echo 2. Check if adapter supports AP mode
    echo 3. Try unplugging and replugging USB adapter
    echo 4. Restart PC and try again
    echo.
    echo ALTERNATIVE: Use phone hotspot with batch rotation
    echo See BATCH-ROTATION-GUIDE.md
    echo.
)

pause
