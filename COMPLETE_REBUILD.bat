@echo off
echo ========================================
echo    TVET QUIZ SYSTEM - COMPLETE REBUILD
echo ========================================
echo.

echo Step 1: Stopping all containers...
docker-compose down -v
docker system prune -f

echo.
echo Step 2: Removing old images...
docker rmi morning_quiz-frontend morning_quiz-backend 2>nul

echo.
echo Step 3: Building fresh containers (no cache)...
docker-compose build --no-cache

echo.
echo Step 4: Starting system...
docker-compose up -d

echo.
echo Step 5: Waiting for services to start...
timeout /t 10 /nobreak

echo.
echo Step 6: Checking system status...
docker ps

echo.
echo ========================================
echo           REBUILD COMPLETE!
echo ========================================
echo.
echo Access your system:
echo - Students: http://localhost:3000
echo - Teachers: http://localhost:3000/teacher
echo - Admin: http://localhost:3000/admin
echo.
echo Default Login:
echo - Admin: admin / admin123
echo - Teacher: teacher001 / teacher123
echo.
echo H5P Card is now visible in Admin Overview!
echo.
pause