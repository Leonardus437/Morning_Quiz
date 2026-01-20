@echo off
echo NETWORK TROUBLESHOOTING - ERR_EMPTY_RESPONSE
echo ============================================
echo.

cd /d "f:\SIDE HUSTLE\Morning_Quiz"

echo [1] Checking port availability...
netstat -an | findstr ":3000"
netstat -an | findstr ":8000"

echo.
echo [2] Checking Docker network...
docker network ls

echo.
echo [3] Inspecting container network settings...
for /f "tokens=*" %%i in ('docker-compose ps -q frontend') do (
    echo Frontend container network:
    docker inspect %%i | findstr "IPAddress"
)

echo.
echo [4] Testing internal container connectivity...
docker-compose exec frontend curl -s http://localhost:5173 || echo "Internal frontend check failed"

echo.
echo [5] Checking Windows Firewall (requires admin)...
netsh advfirewall firewall show rule name="Docker Desktop" >nul 2>&1
if %errorLevel% == 0 (
    echo ✓ Docker firewall rule exists
) else (
    echo ⚠ Docker firewall rule may be missing
    echo Run as Administrator to add firewall rule
)

echo.
echo [6] Alternative access methods:
echo Try these URLs in your browser:
echo - http://127.0.0.1:3000
echo - http://localhost:3000
echo - http://[your-ip]:3000

echo.
echo [7] Container health check...
docker-compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"

echo.
echo [8] Quick restart with port cleanup...
docker-compose down
timeout /t 2 /nobreak >nul
docker-compose up -d --force-recreate

echo.
pause