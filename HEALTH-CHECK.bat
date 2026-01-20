@echo off
echo ========================================
echo TVET Quiz System - Health Check
echo ========================================
echo.

echo [1/8] Checking Docker Desktop...
docker --version >nul 2>&1
if %errorLevel% neq 0 (
    echo    [FAIL] Docker is not installed or not in PATH
    goto :end
) else (
    echo    [OK] Docker is installed
)

echo.
echo [2/8] Checking if Docker is running...
docker ps >nul 2>&1
if %errorLevel% neq 0 (
    echo    [FAIL] Docker Desktop is not running
    echo    Please start Docker Desktop and run this again
    goto :end
) else (
    echo    [OK] Docker Desktop is running
)

echo.
echo [3/8] Checking containers...
docker ps | findstr "tvet_quiz-frontend-1" >nul
if %errorLevel% neq 0 (
    echo    [FAIL] Frontend container not running
) else (
    echo    [OK] Frontend container is running
)

docker ps | findstr "tvet_quiz-backend-1" >nul
if %errorLevel% neq 0 (
    echo    [FAIL] Backend container not running
) else (
    echo    [OK] Backend container is running
)

docker ps | findstr "tvet_quiz-db-1" >nul
if %errorLevel% neq 0 (
    echo    [FAIL] Database container not running
) else (
    echo    [OK] Database container is running
)

echo.
echo [4/8] Checking firewall rules...
netsh advfirewall firewall show rule name="TVET Quiz Port 3000" >nul 2>&1
if %errorLevel% neq 0 (
    echo    [WARNING] Firewall rule for port 3000 not found
    echo    Students may not be able to connect from other devices
) else (
    echo    [OK] Firewall rule for port 3000 exists
)

netsh advfirewall firewall show rule name="TVET Quiz Port 8000" >nul 2>&1
if %errorLevel% neq 0 (
    echo    [WARNING] Firewall rule for port 8000 not found
    echo    Backend may not be accessible from other devices
) else (
    echo    [OK] Firewall rule for port 8000 exists
)

echo.
echo [5/8] Checking network connectivity...
ipconfig | findstr "IPv4" >nul
if %errorLevel% neq 0 (
    echo    [FAIL] No network connection found
) else (
    echo    [OK] Network connection detected
    echo.
    echo    Your IP addresses:
    ipconfig | findstr "IPv4"
)

echo.
echo [6/8] Testing local frontend access...
timeout /t 2 >nul
curl -s http://localhost:3000 >nul 2>&1
if %errorLevel% neq 0 (
    echo    [WARNING] Cannot access frontend at http://localhost:3000
    echo    Frontend may still be starting up
) else (
    echo    [OK] Frontend is accessible at http://localhost:3000
)

echo.
echo [7/8] Testing local backend access...
curl -s http://localhost:8000/health >nul 2>&1
if %errorLevel% neq 0 (
    echo    [WARNING] Cannot access backend at http://localhost:8000
    echo    Backend may still be starting up
) else (
    echo    [OK] Backend is accessible at http://localhost:8000
)

echo.
echo [8/8] Checking ports...
netstat -an | findstr ":3000" | findstr "LISTENING" >nul
if %errorLevel% neq 0 (
    echo    [WARNING] Port 3000 not listening
) else (
    echo    [OK] Port 3000 is listening
)

netstat -an | findstr ":8000" | findstr "LISTENING" >nul
if %errorLevel% neq 0 (
    echo    [WARNING] Port 8000 not listening
) else (
    echo    [OK] Port 8000 is listening
)

echo.
echo ========================================
echo HEALTH CHECK SUMMARY
echo ========================================
echo.

REM Count issues
set ISSUES=0

docker ps >nul 2>&1
if %errorLevel% neq 0 set /a ISSUES+=1

docker ps | findstr "tvet_quiz-frontend-1" >nul
if %errorLevel% neq 0 set /a ISSUES+=1

docker ps | findstr "tvet_quiz-backend-1" >nul
if %errorLevel% neq 0 set /a ISSUES+=1

netsh advfirewall firewall show rule name="TVET Quiz Port 3000" >nul 2>&1
if %errorLevel% neq 0 set /a ISSUES+=1

if %ISSUES% equ 0 (
    echo [SUCCESS] System is healthy and ready to use!
    echo.
    echo Your Quiz System URLs:
    echo - Teacher PC: http://localhost:3000
    echo - Students: http://YOUR_IP:3000
    echo.
    echo Replace YOUR_IP with one of the addresses shown above.
) else (
    echo [WARNING] Found %ISSUES% issue(s)
    echo.
    echo Recommended actions:
    echo 1. Make sure Docker Desktop is running
    echo 2. Run: docker-compose up -d
    echo 3. Run SIMPLE-FIX.bat as Administrator to add firewall rules
)

:end
echo.
echo ========================================
echo Press any key to close...
pause >nul
