@echo off
echo ========================================
echo NETWORK SETUP FOR STUDENT ACCESS
echo ========================================
echo.

echo [1] Finding your PC's IP address...
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4 Address"') do (
    set "ip=%%a"
    set "ip=!ip: =!"
    if not "!ip!"=="" (
        echo ✅ Your PC IP: !ip!
        echo.
        echo 📱 STUDENT ACCESS URL:
        echo http://!ip!:3000
        echo.
        echo Share this URL with students for access from phones/tablets
        goto :found
    )
)

:found
echo.
echo [2] Checking Windows Firewall...
netsh advfirewall firewall show rule name="TVET Quiz Port 3000" >nul 2>&1
if %errorLevel% neq 0 (
    echo Adding firewall rule for port 3000...
    netsh advfirewall firewall add rule name="TVET Quiz Port 3000" dir=in action=allow protocol=TCP localport=3000
    echo ✅ Firewall rule added
) else (
    echo ✅ Firewall rule already exists
)

echo.
echo [3] Testing local access...
curl -s -I http://localhost:3000 | find "200" >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ System is running and accessible
) else (
    echo ❌ System not responding. Please run SETUP-AFTER-FORMAT.bat first
)

echo.
echo ========================================
echo NETWORK TROUBLESHOOTING TIPS:
echo ========================================
echo.
echo If students can't connect:
echo.
echo 1. PUBLIC WIFI ISSUES:
echo    • Public WiFi (like "ednet") often blocks device connections
echo    • SOLUTION: Use your phone's hotspot instead
echo.
echo 2. ROUTER SETUP:
echo    • Buy a cheap WiFi router (₦5,000-10,000)
echo    • Connect your PC via Ethernet cable
echo    • Students connect to router's WiFi
echo.
echo 3. DIRECT HOTSPOT:
echo    • Enable mobile hotspot on your phone
echo    • Connect your PC to the hotspot
echo    • Students connect to same hotspot
echo    • NO INTERNET DATA NEEDED - system works offline!
echo.
echo 4. ETHERNET SHARING:
echo    • Connect PC to router via cable
echo    • Students connect to same router's WiFi
echo.
echo Press any key to continue...
pause >nul