@echo off
echo ========================================
echo Fix Network Access - Morning Quiz
echo ========================================
echo.

echo [1/4] Adding Firewall Rules...
netsh advfirewall firewall delete rule name="Morning Quiz Frontend" > nul 2>&1
netsh advfirewall firewall delete rule name="Morning Quiz Backend" > nul 2>&1

netsh advfirewall firewall add rule name="Morning Quiz Frontend" dir=in action=allow protocol=TCP localport=3000
netsh advfirewall firewall add rule name="Morning Quiz Backend" dir=in action=allow protocol=TCP localport=8000

echo OK: Firewall rules added
echo.

echo [2/4] Checking Docker containers...
docker ps --filter "name=morning" --format "{{.Names}} - {{.Status}}"
echo.

echo [3/4] Testing local access...
curl -s http://localhost:3000 > nul
if %errorlevel% equ 0 (
    echo OK: Frontend accessible locally
) else (
    echo ERROR: Frontend not responding locally
    echo Restarting frontend...
    docker-compose restart frontend
)
echo.

echo [4/4] Getting your IP address...
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4 Address"') do (
    set IP=%%a
    set IP=!IP:~1!
    echo Your IP: !IP!
    echo.
    echo Access URLs:
    echo - Local: http://localhost:3000
    echo - Network: http://!IP!:3000
    echo - Admin: http://!IP!:3000/admin
)
echo.

echo ========================================
echo Network Access Fixed!
echo ========================================
echo.
echo If still can't access from other devices:
echo 1. Ensure devices on same WiFi/LAN
echo 2. Temporarily disable Windows Firewall to test
echo 3. Check antivirus isn't blocking
echo.
pause
