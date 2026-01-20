@echo off
echo QUICK PORT FIX
echo ===============
echo.

cd /d "f:\SIDE HUSTLE\Morning_Quiz"

echo [1] Stopping containers...
docker-compose down

echo.
echo [2] Rebuilding frontend with correct port...
docker-compose build --no-cache frontend

echo.
echo [3] Starting services...
docker-compose up -d

echo.
echo [4] Waiting for startup...
timeout /t 15 /nobreak >nul

echo.
echo [5] Testing connection...
for /l %%i in (1,1,3) do (
    echo Test %%i: http://localhost:3000
    curl -s http://localhost:3000 2>nul | find "html" >nul
    if !errorLevel! == 0 (
        echo ✓ SUCCESS! Open http://localhost:3000 in your browser
        goto :done
    )
    timeout /t 5 /nobreak >nul
)

echo ✗ Still not accessible. Run DIAGNOSE-AND-FIX.bat for detailed analysis.

:done
pause