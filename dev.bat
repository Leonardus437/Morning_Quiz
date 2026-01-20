@echo off
echo Starting Morning Quiz in Development Mode...
docker-compose -f docker-compose.dev.yml down
docker-compose -f docker-compose.dev.yml up -d --build
echo.
echo Development server started!
echo Frontend: http://localhost:3000
echo Backend: http://localhost:8000
echo.
echo Hot reload is enabled - changes will be reflected automatically!
pause