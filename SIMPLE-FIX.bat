@echo off
echo ============================================
echo TVET Quiz - Simple Network Fix
echo ============================================
echo.

REM Check admin
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: Run as Administrator!
    echo.
    echo Right-click this file and select:
    echo "Run as administrator"
    echo.
    echo Press any key to exit...
    pause >nul
    exit
)

echo Step 1: Opening firewall ports...
netsh advfirewall firewall add rule name="TVET Quiz Port 3000" dir=in action=allow protocol=TCP localport=3000
netsh advfirewall firewall add rule name="TVET Quiz Port 8000" dir=in action=allow protocol=TCP localport=8000

echo.
echo Step 2: Finding your IP address...
echo.
ipconfig | findstr "IPv4"

echo.
echo ============================================
echo DONE! Share this URL with students:
echo.
echo http://192.168.61.61:3000
echo.
echo (Replace 192.168.61.61 with YOUR IP from above)
echo ============================================
echo.
echo Press any key to close...
pause >nul
