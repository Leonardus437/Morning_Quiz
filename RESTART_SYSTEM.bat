@echo off
<<<<<<< HEAD
echo Restarting Docker containers...
echo.
docker-compose down
docker-compose up -d
echo.
echo Done! System restarted.
echo Open http://localhost:3000 to test
pause
=======
echo Restarting Morning Quiz System...
echo.

echo Stopping containers...
docker-compose down

echo Clearing Docker cache...
docker system prune -f

echo Starting system with fresh build...
docker-compose up -d --build

echo.
echo System restarted successfully!
echo Access the system at: http://localhost:3000
echo.
pause
>>>>>>> a6f256911bd91da0b979b46a8d9484a08d4142a9
