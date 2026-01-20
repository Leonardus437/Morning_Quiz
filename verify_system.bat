@echo off
echo ========================================
<<<<<<< HEAD
echo   TVET QUIZ SYSTEM - VERIFICATION
echo ========================================
echo.

echo [1/5] Checking Docker containers...
docker ps --format "table {{.Names}}\t{{.Status}}"
echo.

echo [2/5] Verifying AI Parser module...
docker exec tvet_quiz-backend-1 python -c "from ai_parser import AIStudentParser; print('✅ AI Parser: OK')" 2>nul
if %errorlevel% neq 0 (
    echo ❌ AI Parser: FAILED
) else (
    echo ✅ AI Parser: LOADED
)
echo.

echo [3/5] Checking Frontend...
curl -s http://localhost:3000 >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Frontend: NOT ACCESSIBLE
) else (
    echo ✅ Frontend: ACCESSIBLE at http://localhost:3000
)
echo.

echo [4/5] Checking Backend API...
curl -s http://localhost:8000/docs >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Backend: NOT ACCESSIBLE
) else (
    echo ✅ Backend: ACCESSIBLE at http://localhost:8000
)
echo.

echo [5/5] Checking Database...
docker exec tvet_quiz-db-1 pg_isready -U tvet_user >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Database: NOT READY
) else (
    echo ✅ Database: READY
=======
echo Morning Quiz System Health Check
echo ========================================
echo.

echo [1/6] Testing Backend Health...
curl -s https://tvet-quiz-backend.onrender.com/health
if %errorlevel% neq 0 (
    echo ❌ Backend is NOT responding
    echo    - Check if Render service is running
    echo    - Visit: https://dashboard.render.com
) else (
    echo ✅ Backend is responding
)
echo.

echo [2/6] Testing Local Docker Services...
docker ps --filter "name=tvet_quiz" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
if %errorlevel% neq 0 (
    echo ⚠️  Docker services not running locally
    echo    - Run: docker-compose up -d
) else (
    echo ✅ Docker services are running
)
echo.

echo [3/6] Checking Database Connection...
docker exec tvet_quiz-db-1 psql -U quiz_user -d morning_quiz -c "SELECT COUNT(*) as user_count FROM users;" 2>nul
if %errorlevel% neq 0 (
    echo ⚠️  Cannot connect to database
    echo    - Ensure Docker is running
    echo    - Run: docker-compose up -d
) else (
    echo ✅ Database is accessible
)
echo.

echo [4/6] Testing Local Backend...
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Local backend not responding
    echo    - Run: docker-compose up -d
) else (
    echo ✅ Local backend is running
)
echo.

echo [5/6] Testing Local Frontend...
curl -s http://localhost:3000 >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Local frontend not responding
    echo    - Run: cd frontend && npm run dev
) else (
    echo ✅ Local frontend is running
)
echo.

echo [6/6] Checking Required Files...
if exist "backend\main.py" (
    echo ✅ Backend main.py exists
) else (
    echo ❌ Backend main.py missing
)

if exist "frontend\package.json" (
    echo ✅ Frontend package.json exists
) else (
    echo ❌ Frontend package.json missing
)

if exist "docker-compose.yml" (
    echo ✅ docker-compose.yml exists
) else (
    echo ❌ docker-compose.yml missing
)

if exist "render.yaml" (
    echo ✅ render.yaml exists
) else (
    echo ❌ render.yaml missing
>>>>>>> a6f256911bd91da0b979b46a8d9484a08d4142a9
)
echo.

echo ========================================
<<<<<<< HEAD
echo   VERIFICATION COMPLETE
echo ========================================
echo.
echo Access Points:
echo   Teacher Panel: http://localhost:3000/teacher
echo   Admin Panel:   http://localhost:3000/admin
echo   Student Login: http://localhost:3000
echo   API Docs:      http://localhost:8000/docs
echo.
echo Default Login:
echo   Username: teacher001
echo   Password: teacher123
=======
echo Health Check Complete
echo ========================================
echo.
echo NEXT STEPS:
echo 1. If backend is down, check Render dashboard
echo 2. If local services are down, run: docker-compose up -d
echo 3. Review SYSTEM_HEALTH_CHECK.md for detailed analysis
>>>>>>> a6f256911bd91da0b979b46a8d9484a08d4142a9
echo.
pause
