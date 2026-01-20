@echo off
echo COMPREHENSIVE SYSTEM DIAGNOSTIC
echo =================================
echo.

cd /d "f:\SIDE HUSTLE\Morning_Quiz"

echo [1] Current Directory Check...
echo Current path: %cd%
echo.

echo [2] Docker Container Status...
docker-compose ps
echo.

echo [3] Port Mapping Check...
echo Checking what ports are actually being used:
netstat -an | findstr :3000
netstat -an | findstr :5173
netstat -an | findstr :8000
echo.

echo [4] Frontend Container Details...
docker inspect tvet_quiz-frontend-1 --format="{{.NetworkSettings.Ports}}"
echo.

echo [5] All Container Port Mappings...
docker port tvet_quiz-frontend-1
docker port tvet_quiz-backend-1
docker port tvet_quiz-db-1
echo.

echo [6] Frontend Logs (Last 30 lines)...
docker-compose logs frontend --tail=30
echo.

echo [7] Testing All Possible URLs...
echo Testing http://localhost:3000
curl -I http://localhost:3000 2>nul
echo.
echo Testing http://localhost:5173
curl -I http://localhost:5173 2>nul
echo.
echo Testing http://localhost:8000
curl -I http://localhost:8000 2>nul
echo.

echo [8] Docker Compose File Check...
echo Checking if docker-compose.yml has correct port mappings:
findstr "ports:" docker-compose.yml
findstr "3000" docker-compose.yml
findstr "5173" docker-compose.yml
echo.

echo [9] Container Internal Network...
docker network ls
echo.

echo [10] SOLUTION ATTEMPTS...
echo Attempting to fix port mapping issue...
docker-compose down
echo Rebuilding with correct ports...
docker-compose up -d --force-recreate
echo.

echo [11] Final Test After Fix...
timeout /t 15 /nobreak >nul
echo Testing URLs again:
curl -s -o nul -w "%%{http_code}" http://localhost:3000
echo " - localhost:3000"
curl -s -o nul -w "%%{http_code}" http://localhost:5173  
echo " - localhost:5173"
curl -s -o nul -w "%%{http_code}" http://localhost:8000
echo " - localhost:8000"
echo.

echo [12] WORKING URLS:
echo Try these URLs in your browser:
echo - http://localhost:3000
echo - http://localhost:3000/teacher  
echo - http://localhost:5173
echo - http://localhost:5173/teacher
echo - http://localhost:8000
echo.

pause