@echo off
echo EMERGENCY FIX - ERR_EMPTY_RESPONSE
echo ===================================
echo.

cd /d "f:\SIDE HUSTLE\Morning_Quiz"

echo [1] Stopping all containers...
docker-compose down

echo.
echo [2] Checking frontend Dockerfile...
if exist "frontend\Dockerfile" (
    echo ✓ Frontend Dockerfile exists
) else (
    echo ✗ Frontend Dockerfile missing - CREATING IT NOW
    echo FROM node:18-alpine as build > frontend\Dockerfile
    echo WORKDIR /app >> frontend\Dockerfile
    echo COPY package*.json ./ >> frontend\Dockerfile
    echo RUN npm ci --only=production >> frontend\Dockerfile
    echo COPY . . >> frontend\Dockerfile
    echo RUN npm run build >> frontend\Dockerfile
    echo FROM node:18-alpine as production >> frontend\Dockerfile
    echo WORKDIR /app >> frontend\Dockerfile
    echo COPY --from=build /app . >> frontend\Dockerfile
    echo EXPOSE 5173 >> frontend\Dockerfile
    echo CMD ["npm", "run", "preview", "--", "--host", "0.0.0.0", "--port", "5173"] >> frontend\Dockerfile
)

echo.
echo [3] Rebuilding frontend container from scratch...
docker-compose build --no-cache frontend

echo.
echo [4] Starting all services...
docker-compose up -d

echo.
echo [5] Waiting for services to initialize...
timeout /t 30 /nobreak >nul

echo.
echo [6] Checking container status...
docker-compose ps

echo.
echo [7] Checking frontend logs...
docker-compose logs frontend --tail=20

echo.
echo [8] Testing connection...
curl -v http://localhost:3000 2>&1 | findstr "Connected\|HTTP\|Error"

echo.
echo [9] ALTERNATIVE: Try direct container access...
echo If localhost:3000 still fails, try:
echo - http://127.0.0.1:3000
echo - Check Windows Firewall
echo - Try different browser

echo.
echo [10] Manual container restart if needed...
docker-compose restart frontend

echo.
pause