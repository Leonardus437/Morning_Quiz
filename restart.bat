@echo off
echo Starting Docker Desktop...
start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
echo Waiting for Docker to be ready...
timeout /t 15 /nobreak
echo Stopping existing containers...
docker-compose down
echo Starting backend and frontend...
docker-compose up -d
echo.
echo Services started! Waiting for them to be ready...
timeout /t 5 /nobreak
echo.
echo Frontend: http://localhost:3000
echo Backend: http://localhost:8000
echo.
pause
