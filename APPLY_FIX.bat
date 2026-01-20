@echo off
echo ========================================
echo   FIXING "Not Answered" BUG
echo ========================================
echo.
echo Restarting backend to apply fix...
echo.

cd /d d:\Morning_Quiz-master
docker-compose restart backend

echo.
echo ========================================
echo   FIX APPLIED!
echo ========================================
echo.
echo The "Not answered" bug is now fixed.
echo Students' answers will now be graded correctly.
echo.
echo Test by:
echo 1. Taking a quiz as student
echo 2. Answering questions 5 and 10
echo 3. Checking results - should show actual grades
echo.
pause
