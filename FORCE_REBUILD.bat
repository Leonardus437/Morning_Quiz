@echo off
color 0C
echo ========================================
echo   FORCE REBUILD - CLEAR ALL CACHES
echo ========================================
echo.
echo This will:
echo   1. Stop all containers
echo   2. Remove old build files
echo   3. Rebuild frontend
echo   4. Restart everything
echo.
pause

echo.
echo [1/5] Stopping containers...
docker-compose down

echo.
echo [2/5] Removing old frontend build...
docker exec tvet_quiz-frontend-1 rm -rf /app/build 2>nul
docker exec tvet_quiz-frontend-1 rm -rf /app/.svelte-kit 2>nul

echo.
echo [3/5] Starting containers...
docker-compose up -d

echo.
echo [4/5] Waiting for frontend to rebuild...
timeout /t 15

echo.
echo [5/5] Checking status...
docker-compose ps

echo.
echo ========================================
echo   REBUILD COMPLETE!
echo ========================================
echo.
echo CRITICAL: You MUST clear browser cache NOW:
echo.
echo   1. Close ALL browser windows
echo   2. Reopen browser
echo   3. Press Ctrl+Shift+Delete
echo   4. Select "All time"
echo   5. Check "Cached images and files"
echo   6. Check "Cookies and site data"
echo   7. Click "Clear data"
echo   8. Go to http://localhost:3000/admin
echo   9. Press F12, go to Application tab
echo  10. Click "Service Workers"
echo  11. Click "Unregister" for localhost:3000
echo  12. Close browser again
echo  13. Reopen and test
echo.
echo OR use Incognito mode (Ctrl+Shift+N)
echo.
pause
