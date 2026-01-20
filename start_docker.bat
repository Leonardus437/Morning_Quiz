@echo off
echo Starting Docker Desktop...
start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
echo Waiting for Docker to start...
timeout /t 30 /nobreak
echo Docker should be ready now!
echo.
echo Starting TVET Quiz System...
docker-compose build
docker-compose up -d
echo.
echo System ready at http://localhost:3000
pause