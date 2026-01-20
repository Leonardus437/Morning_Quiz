@echo off
echo ========================================
echo   PC Hotspot Capability Check
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

echo [1/3] Checking if your PC supports WiFi hotspot...
echo.

netsh wlan show drivers | findstr /C:"Hosted network supported"

if %errorLevel% equ 0 (
    echo.
    echo ========================================
    echo   ✅ YES! Your PC supports hotspot!
    echo ========================================
    echo.
    echo CAPACITY: 20-100 devices (depends on WiFi adapter)
    echo TYPICAL: 30-50 devices work well
    echo.
    echo This is MUCH BETTER than phone hotspot (10 devices)!
    echo.
    echo [2/3] Current WiFi adapter details:
    echo.
    netsh wlan show drivers | findstr /C:"Description" /C:"Max number"
    echo.
    echo [3/3] Would you like to create hotspot now? (Y/N)
    set /p choice=Enter choice: 
    
    if /i "%choice%"=="Y" (
        echo.
        echo Creating hotspot...
        netsh wlan set hostednetwork mode=allow ssid=TVETQuiz key=quiz12345
        netsh wlan start hostednetwork
        
        if %errorLevel% equ 0 (
            echo.
            echo ========================================
            echo   SUCCESS! PC Hotspot is running
            echo ========================================
            echo.
            echo HOTSPOT DETAILS:
            echo   Network Name: TVETQuiz
            echo   Password: quiz12345
            echo   Capacity: 30-50 devices
            echo.
            echo YOUR PC IP ADDRESS:
            ipconfig | findstr /C:"IPv4" | findstr /C:"192.168"
            echo.
            echo STUDENT ACCESS:
            echo   1. Connect to WiFi: TVETQuiz
            echo   2. Open browser
            echo   3. Go to: http://192.168.137.1:3000
            echo.
            echo ========================================
            echo   You can now handle 60+ students!
            echo ========================================
            echo.
        ) else (
            echo.
            echo ERROR: Could not start hotspot
            echo Try disabling and re-enabling WiFi adapter
            echo.
        )
    )
) else (
    echo.
    echo ========================================
    echo   ❌ NO - Your PC does NOT support hotspot
    echo ========================================
    echo.
    echo REASON: WiFi adapter doesn't support "Hosted Network"
    echo.
    echo YOUR OPTIONS:
    echo 1. Use phone hotspot with batch rotation (FREE)
    echo 2. Buy USB WiFi adapter with AP mode (~5,000 RWF)
    echo 3. Buy WiFi router (~8,000 RWF)
    echo.
    echo RECOMMENDED: Option 1 (phone hotspot + rotation)
    echo See BATCH-ROTATION-GUIDE.md for details
    echo.
)

echo.
pause
