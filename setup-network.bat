@echo off
echo ========================================
echo TVET Quiz System - Network Setup
echo ========================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: This script must be run as Administrator!
    echo Right-click and select "Run as administrator"
    pause
    exit /b 1
)

echo [1/4] Adding Windows Firewall rules...
netsh advfirewall firewall delete rule name="TVET Quiz Port 3000" >nul 2>&1
netsh advfirewall firewall delete rule name="TVET Quiz Port 8000" >nul 2>&1
netsh advfirewall firewall add rule name="TVET Quiz Port 3000" dir=in action=allow protocol=TCP localport=3000
netsh advfirewall firewall add rule name="TVET Quiz Port 8000" dir=in action=allow protocol=TCP localport=8000
echo    Firewall rules added successfully!

echo.
echo [2/4] Detecting your IP address...
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4 Address"') do (
    set IP=%%a
    set IP=!IP:~1!
    echo    Found IP: !IP!
    goto :found_ip
)
:found_ip

echo.
echo [3/4] Restarting Docker containers...
cd /d "%~dp0"
docker-compose down
docker-compose up -d --build

echo.
echo [4/4] Setup complete!
echo.
echo ========================================
echo IMPORTANT: Share this URL with students
echo ========================================
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4 Address"') do (
    set IP=%%a
    set IP=!IP:~1!
    echo.
    echo    http://!IP!:3000
    echo.
)
echo ========================================
echo.
echo NOTE: If using public WiFi (like ednet),
echo you may need to:
echo 1. Use your phone hotspot instead
echo 2. Contact network admin to disable AP isolation
echo 3. Use a dedicated router for the quiz system
echo.
pause
