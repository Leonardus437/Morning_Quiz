@echo off
echo ========================================
echo TVET Quiz System - Enable LAN Access
echo ========================================
echo.

REM Check for admin rights
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: This script must be run as Administrator!
    echo Right-click this file and select "Run as administrator"
    pause
    exit /b 1
)

echo [1/4] Adding Windows Firewall rule for port 3000...
netsh advfirewall firewall delete rule name="TVET Quiz System" >nul 2>&1
netsh advfirewall firewall add rule name="TVET Quiz System" dir=in action=allow protocol=TCP localport=3000
if %errorLevel% equ 0 (
    echo     SUCCESS: Port 3000 opened in firewall
) else (
    echo     WARNING: Could not add firewall rule
)

echo.
echo [2/4] Adding Windows Firewall rule for port 8000...
netsh advfirewall firewall delete rule name="TVET Quiz Backend" >nul 2>&1
netsh advfirewall firewall add rule name="TVET Quiz Backend" dir=in action=allow protocol=TCP localport=8000
if %errorLevel% equ 0 (
    echo     SUCCESS: Port 8000 opened in firewall
) else (
    echo     WARNING: Could not add firewall rule
)

echo.
echo [3/4] Getting your PC's IP address...
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /C:"IPv4 Address"') do (
    set IP=%%a
    goto :found
)
:found
set IP=%IP:~1%
echo     Your PC IP: %IP%

echo.
echo [4/4] Verifying Docker containers...
docker ps --format "{{.Names}}: {{.Status}}"

echo.
echo ========================================
echo LAN ACCESS ENABLED!
echo ========================================
echo.
echo Students can now access the system at:
echo.
echo     http://%IP%:3000
echo.
echo Share this URL with your students!
echo.
echo Teacher/Admin access (on this PC):
echo     http://localhost:3000/teacher
echo     http://localhost:3000/admin
echo.
echo ========================================
pause
