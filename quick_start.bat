@echo off
echo Starting TVET Quiz System...
echo.
echo Step 1: Building images...
docker-compose build
echo.
echo Step 2: Starting services...
docker-compose up -d
echo.
echo System ready! Access at:
echo - Teacher: http://localhost:3000/teacher
echo - Admin: http://localhost:3000/admin
echo - Students: http://localhost:3000
echo.
pause