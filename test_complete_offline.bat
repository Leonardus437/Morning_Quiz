@echo off
echo ================================================
echo COMPLETE OFFLINE FUNCTIONALITY TEST
echo ================================================
echo.

echo [STEP 1] Starting system...
docker-compose -f docker-compose.offline.yml up -d

echo.
echo [STEP 2] Waiting for services to initialize...
timeout /t 15 /nobreak >nul

echo.
echo [STEP 3] Testing basic connectivity...
curl -s -o nul -w "Frontend: HTTP %%{http_code}" http://localhost:3000
echo.
curl -s http://localhost:8000/health
echo.

echo.
echo [STEP 4] Getting your PC IP address...
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr "IPv4" ^| findstr "192.168"') do (
    set IP=%%a
    set IP=!IP: =!
    echo Your PC IP: !IP!
    echo LAN URL: http://!IP!:3000
)

echo.
echo [STEP 5] Testing LAN access...
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr "IPv4" ^| findstr "192.168"') do (
    set IP=%%a
    set IP=!IP: =!
    curl -s -o nul -w "LAN Access: HTTP %%{http_code}" http://!IP!:3000
    echo.
)

echo.
echo [STEP 6] Testing offline components...
curl -s -o nul -w "Service Worker: HTTP %%{http_code}" http://localhost:3000/sw.js
echo.
curl -s -o nul -w "PWA Manifest: HTTP %%{http_code}" http://localhost:3000/manifest.json
echo.
curl -s -o nul -w "Offline Page: HTTP %%{http_code}" http://localhost:3000/offline.html
echo.

echo.
echo ================================================
echo MANUAL TESTING INSTRUCTIONS
echo ================================================
echo.
echo 1. Open browser and go to: http://localhost:3000
echo 2. Login with: admin / admin123
echo 3. Navigate to different pages (teacher, admin)
echo 4. Open browser DevTools (F12) and go to Network tab
echo 5. Check "Offline" checkbox to simulate no internet
echo 6. Refresh page - should still work
echo 7. Try creating a quiz or navigating - should work offline
echo.
echo FOR LAN TESTING:
echo 8. On another device, connect to same WiFi
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr "IPv4" ^| findstr "192.168"') do (
    set IP=%%a
    set IP=!IP: =!
    echo 9. Open: http://!IP!:3000
)
echo 10. Should work without internet on the host PC
echo.
pause