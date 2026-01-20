@echo off
echo Testing Offline Functionality
echo ============================

echo.
echo 1. Starting system in offline mode...
call start-offline.bat

echo.
echo 2. Waiting for services to be ready...
timeout /t 15 /nobreak >nul

echo.
echo 3. Testing service worker registration...
curl -s http://localhost:3000/sw.js > nul
if %errorlevel% == 0 (
    echo ✅ Service Worker accessible
) else (
    echo ❌ Service Worker not accessible
)

echo.
echo 4. Testing manifest.json...
curl -s http://localhost:3000/manifest.json > nul
if %errorlevel% == 0 (
    echo ✅ PWA Manifest accessible
) else (
    echo ❌ PWA Manifest not accessible
)

echo.
echo 5. Testing backend health...
curl -s http://localhost:8000/health > nul
if %errorlevel% == 0 (
    echo ✅ Backend health check passed
) else (
    echo ❌ Backend health check failed
)

echo.
echo 6. Testing database connection...
docker exec morning_quiz-db-1 pg_isready -U quiz_user -d morning_quiz > nul 2>&1
if %errorlevel% == 0 (
    echo ✅ Database connection successful
) else (
    echo ❌ Database connection failed
)

echo.
echo ==========================================
echo Offline functionality test completed!
echo.
echo Access the system at:
echo - http://localhost:3000 (Students)
echo - http://localhost:3000/teacher (Teachers)
echo - http://localhost:3000/admin (Admin)
echo.
pause