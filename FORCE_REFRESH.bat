@echo off
echo Forcing complete system refresh...
echo.

echo 1. Killing all processes on ports 3000 and 8000...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :3000') do taskkill /f /pid %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do taskkill /f /pid %%a >nul 2>&1

echo 2. Stopping Docker containers...
docker-compose down --remove-orphans

echo 3. Clearing Docker cache...
docker system prune -af --volumes

echo 4. Rebuilding with no cache...
docker-compose build --no-cache --pull

echo 5. Starting fresh system...
docker-compose up -d

echo.
echo System rebuilt! Access at http://localhost:3000/admin
pause