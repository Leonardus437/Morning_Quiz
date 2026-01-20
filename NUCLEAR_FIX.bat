@echo off
echo ========================================
echo NUCLEAR FIX - Complete System Reset
echo ========================================
echo.

echo Step 1: Stopping all containers...
docker-compose down
timeout /t 3 /nobreak >nul

echo.
echo Step 2: Removing frontend image...
docker rmi morning_quiz-frontend 2>nul

echo.
echo Step 3: Cleaning Docker system...
docker system prune -f

echo.
echo Step 4: Starting system (will rebuild)...
docker-compose up -d --build

echo.
echo ========================================
echo WAITING FOR SYSTEM TO START (30 seconds)...
echo ========================================
timeout /t 30 /nobreak

echo.
echo ========================================
echo NOW DO THIS IN YOUR BROWSER:
echo ========================================
echo.
echo 1. Press F12 to open Developer Tools
echo 2. Go to "Application" tab
echo 3. Click "Service Workers" on the left
echo 4. Click "Unregister" next to the service worker
echo 5. Click "Clear storage" on the left
echo 6. Click "Clear site data" button
echo 7. Close browser completely
echo 8. Open browser again and go to: http://localhost:3000/admin
echo.
echo ========================================
echo OR SIMPLY: Use Incognito/Private mode!
echo ========================================
echo Chrome: Ctrl + Shift + N
echo Firefox: Ctrl + Shift + P
echo Edge: Ctrl + Shift + N
echo.
pause
