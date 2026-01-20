@echo off
echo ========================================
echo TVET QUIZ SYSTEM - POST-FORMAT SETUP
echo ========================================
echo.

cd /d "f:\SIDE HUSTLE\Morning_Quiz"

echo [STEP 1] Checking Docker Desktop...
docker --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ Docker Desktop not found!
    echo.
    echo Please install Docker Desktop first:
    echo 1. Download from: https://www.docker.com/products/docker-desktop/
    echo 2. Install and restart your computer
    echo 3. Run this script again
    echo.
    pause
    exit /b 1
) else (
    echo ✅ Docker Desktop found
)

echo.
echo [STEP 2] Checking Docker service...
docker info >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ Docker service not running!
    echo.
    echo Please start Docker Desktop and wait for it to fully load
    echo Then run this script again
    echo.
    pause
    exit /b 1
) else (
    echo ✅ Docker service running
)

echo.
echo [STEP 3] Stopping any existing containers...
docker-compose down -v

echo.
echo [STEP 4] Cleaning up old images and containers...
docker system prune -f

echo.
echo [STEP 5] Building fresh containers...
docker-compose build --no-cache

echo.
echo [STEP 6] Starting the system...
docker-compose up -d

echo.
echo [STEP 7] Waiting for services to initialize...
timeout /t 30 /nobreak >nul

echo.
echo [STEP 8] Checking service status...
docker-compose ps

echo.
echo [STEP 9] Testing database connection...
timeout /t 10 /nobreak >nul
docker-compose exec -T db psql -U quiz_user -d morning_quiz -c "SELECT COUNT(*) FROM users;" >nul 2>&1
if %errorLevel% neq 0 (
    echo ⚠️  Database still initializing, this is normal on first run
) else (
    echo ✅ Database connected successfully
)

echo.
echo [STEP 10] Testing frontend...
for /l %%i in (1,1,5) do (
    echo Testing connection attempt %%i/5...
    curl -s -I http://localhost:3000 | find "200" >nul 2>&1
    if !errorLevel! == 0 (
        echo ✅ Frontend responding!
        goto :success
    )
    timeout /t 5 /nobreak >nul
)

echo ⚠️  Frontend may still be starting up

:success
echo.
echo ========================================
echo 🎉 SETUP COMPLETE!
echo ========================================
echo.
echo ACCESS URLS:
echo • Student Login: http://localhost:3000
echo • Teacher Panel: http://localhost:3000/teacher
echo • Admin Panel:   http://localhost:3000/admin
echo.
echo DEFAULT CREDENTIALS:
echo.
echo 👨‍💼 ADMIN:
echo   Username: admin
echo   Password: pass123
echo.
echo 👩‍🏫 TEACHERS:
echo   Username: teacher001  Password: pass123
echo   Username: teacher002  Password: pass123
echo   Username: teacher003  Password: pass123
echo.
echo 👨‍🎓 STUDENTS:
echo   Username: student001  Password: pass123
echo   Username: student002  Password: pass123
echo   Username: student003  Password: pass123
echo   Username: student004  Password: pass123
echo   Username: student005  Password: pass123
echo   Username: student006  Password: pass123
echo   Username: student007  Password: pass123
echo   Username: student008  Password: pass123
echo.
echo NETWORK ACCESS:
echo Run 'ipconfig' to find your IP address
echo Share http://[YOUR-IP]:3000 with students
echo.
echo DAILY USAGE:
echo • Start: docker-compose up -d
echo • Stop:  docker-compose down
echo.
echo Press any key to continue...
pause >nul