@echo off
setlocal enabledelayedexpansion
echo COMPREHENSIVE DIAGNOSIS AND FIX
echo ================================
echo.

cd /d "f:\SIDE HUSTLE\Morning_Quiz"

echo [1] Checking Docker containers...
docker-compose ps
echo.

echo [2] Getting detailed frontend logs...
docker-compose logs frontend --tail=20
echo.

echo [3] Checking port bindings...
docker port tvet_quiz-frontend-1
echo.

echo [4] Testing internal container connectivity...
docker exec tvet_quiz-frontend-1 curl -s -I http://localhost:5173 2>nul
echo.

echo [5] Checking Windows port usage...
netstat -ano | findstr :3000
echo.

echo [6] Testing direct container IP...
for /f "tokens=*" %%i in ('docker inspect -f "{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}" tvet_quiz-frontend-1') do set CONTAINER_IP=%%i
echo Container IP: !CONTAINER_IP!
if not "!CONTAINER_IP!"=="" (
    echo Testing http://!CONTAINER_IP!:5173
    curl -s -I http://!CONTAINER_IP!:5173 2>nul
)
echo.

echo [7] EMERGENCY FIX - Recreate with explicit port mapping...
docker-compose down
docker-compose up -d --force-recreate
timeout /t 10 /nobreak >nul

echo.
echo [8] Final connectivity test...
for /l %%i in (1,1,5) do (
    echo Test %%i/5: http://localhost:3000
    curl -s -I http://localhost:3000 2>nul | find "200"
    if !errorLevel! == 0 (
        echo ✓ SUCCESS! Application accessible at http://localhost:3000
        goto :success
    )
    timeout /t 3 /nobreak >nul
)

echo.
echo [9] Alternative access methods...
echo Try these URLs in your browser:
echo - http://localhost:3000
echo - http://127.0.0.1:3000
echo - http://!CONTAINER_IP!:5173 (if container IP found)
echo.
echo If none work, check:
echo - Windows Firewall (disable temporarily)
echo - Antivirus software blocking ports
echo - Try different browser
echo - Run as Administrator

:success
echo.
pause