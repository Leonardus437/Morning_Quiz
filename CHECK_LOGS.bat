@echo off
echo ========================================
echo   CHECKING QUIZ SUBMISSION
echo ========================================
echo.
echo Showing last 30 backend log lines...
echo.

cd /d d:\Morning_Quiz-master
docker-compose logs backend --tail 30

echo.
echo ========================================
echo.
echo Look for:
echo - "Quiz submission started"
echo - "Found X questions"
echo - "Grading complete. Score: X/Y"
echo.
pause
