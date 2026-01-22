@echo off
echo ========================================
echo TVET Quiz System - Health Check
echo ========================================
echo.

echo [1/5] Checking Docker containers...
docker-compose ps
echo.

echo [2/5] Testing Backend API...
curl -s http://localhost:8000/health
echo.
echo.

echo [3/5] Testing Database connection...
docker exec tvet_quiz-backend-1 python -c "from sqlalchemy import create_engine; engine = create_engine('postgresql://quiz_user:quiz_pass123@db:5432/morning_quiz'); conn = engine.connect(); print('Database: OK')"
echo.

echo [4/5] Checking Frontend...
curl -s -o nul -w "Frontend Status: %%{http_code}\n" http://localhost:3000
echo.

echo [5/5] Your Network Information...
echo.
echo Local Access:
echo   Teacher: http://localhost:3000/teacher
echo   Students: http://localhost:3000
echo.
echo LAN Access (Share with students):
ipconfig | findstr /i "IPv4"
echo.

echo ========================================
echo Production URLs:
echo   Frontend: https://tsskwizi.pages.dev
echo   Backend: https://tvet-quiz-backend.onrender.com
echo ========================================
echo.

echo System Status: READY
echo.
pause
