@echo off
echo ========================================
echo   APPLYING STUDENT PERFORMANCE FIX
echo ========================================
echo.
echo This will restart the backend to enable:
echo - Student performance tracking
echo - Quiz report downloads
echo.
pause

echo.
echo [1/3] Stopping containers...
docker-compose down

echo.
echo [2/3] Rebuilding backend...
docker-compose build backend

echo.
echo [3/3] Starting system...
docker-compose up -d

echo.
echo ========================================
echo   FIX APPLIED SUCCESSFULLY!
echo ========================================
echo.
echo Students can now:
echo - View their performance at /performance
echo - Download detailed quiz reports
echo.
echo Test it:
echo 1. Login as a student who completed a quiz
echo 2. Go to "My Performance" page
echo 3. Click "Download Detailed Report"
echo.
pause
