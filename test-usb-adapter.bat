@echo off
echo ========================================
echo   USB WiFi Adapter Capability Test
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

echo [TEST 1/3] Checking all WiFi adapters...
echo.
echo ========================================
netsh wlan show drivers
echo ========================================
echo.
echo LOOK FOR:
echo   - "Hosted network supported : Yes" (MUST be Yes!)
echo   - Check which adapter shows "Yes"
echo   - Note the adapter name/description
echo.
pause

echo.
echo [TEST 2/3] Attempting to create hotspot...
echo.

netsh wlan set hostednetwork mode=allow ssid=TEST_HOTSPOT key=test12345

if %errorLevel% equ 0 (
    echo ✅ Hotspot configuration created successfully!
    echo.
    echo [TEST 3/3] Attempting to start hotspot...
    echo.
    
    netsh wlan start hostednetwork
    
    if %errorLevel% equ 0 (
        echo.
        echo ========================================
        echo   ✅ SUCCESS! Your USB adapter works!
        echo ========================================
        echo.
        echo Your USB WiFi adapter SUPPORTS hotspot mode!
        echo.
        echo NEXT STEPS:
        echo 1. Connect multiple devices to test capacity
        echo 2. WiFi Name: TEST_HOTSPOT
        echo 3. Password: test12345
        echo.
        echo TEST CAPACITY:
        echo - Connect your phone
        echo - Connect colleague's phones
        echo - Connect laptops
        echo - Count how many can connect
        echo.
        echo TYPICAL CAPACITY: 30-50 devices
        echo.
        echo Press any key to stop test hotspot...
        pause >nul
        
        echo.
        echo Stopping test hotspot...
        netsh wlan stop hostednetwork
        
        echo.
        echo ========================================
        echo   TEST COMPLETE - ADAPTER WORKS!
        echo ========================================
        echo.
        echo YOUR ADAPTER CAN:
        echo ✅ Create WiFi hotspot
        echo ✅ Support 30-50+ devices
        echo ✅ Handle your 60 students (2 batches)
        echo.
        echo READY TO USE:
        echo Run: setup-usb-hotspot.bat
        echo.
    ) else (
        echo.
        echo ========================================
        echo   ❌ FAILED: Could not start hotspot
        echo ========================================
        echo.
        echo POSSIBLE REASONS:
        echo 1. USB adapter doesn't support AP mode
        echo 2. Drivers not installed properly
        echo 3. Another hotspot is running
        echo 4. WiFi adapter is disabled
        echo.
        echo SOLUTIONS TO TRY:
        echo.
        echo A. Update USB WiFi adapter drivers:
        echo    - Device Manager
        echo    - Network Adapters
        echo    - Right-click USB adapter
        echo    - Update Driver
        echo.
        echo B. Try different USB port:
        echo    - Unplug USB adapter
        echo    - Plug into different USB port
        echo    - Run this test again
        echo.
        echo C. Restart PC and try again
        echo.
        echo D. Check adapter model:
        echo    - Some cheap adapters don't support AP mode
        echo    - Check manufacturer specifications
        echo.
        echo IF ADAPTER DOESN'T WORK:
        echo Use phone hotspot with batch rotation (FREE)
        echo See: BATCH-ROTATION-GUIDE.md
        echo.
    )
) else (
    echo.
    echo ========================================
    echo   ❌ FAILED: Configuration error
    echo ========================================
    echo.
    echo Your USB adapter may not support hotspot mode.
    echo.
    echo ALTERNATIVE SOLUTIONS:
    echo 1. Phone hotspot + batch rotation (FREE)
    echo 2. Buy different USB adapter with AP mode
    echo 3. Buy WiFi router (8,000 RWF)
    echo.
)

pause
