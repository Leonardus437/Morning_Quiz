@echo off
echo ========================================
echo TVET QUIZ SYSTEM - DAILY STARTUP
echo ========================================
echo.

cd /d "f:\SIDE HUSTLE\Morning_Quiz"

echo Starting the quiz system...
docker-compose up -d

echo.
echo Waiting for services to load...
timeout /t 15 /nobreak >nul

echo.
echo Checking system status...
docker-compose ps

echo.
echo Testing connection...
curl -s -I http://localhost:3000 | find "200" >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ System is ready!
) else (
    echo ⚠️  System still starting up...
)

echo.
echo ========================================
echo 🎉 QUIZ SYSTEM READY!
echo ========================================
echo.
echo 📱 ACCESS URLS:
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4 Address"') do (
    set "ip=%%a"
    set "ip=!ip: =!"
    if not "!ip!"=="" (
        echo • Students: http://!ip!:3000
        goto :showlocal
    )
)

:showlocal
echo • Teachers: http://localhost:3000/teacher
echo • Admin:    http://localhost:3000/admin
echo.
echo 🔑 Quick Login (all passwords: pass123):
echo • Admin: admin
echo • Teachers: teacher001, teacher002, teacher003  
echo • Students: student001 to student008
echo.
echo 🛑 To stop system: docker-compose down
echo.
echo Press any key to continue...
pause >nul