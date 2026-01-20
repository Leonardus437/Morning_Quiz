@echo off
echo ========================================
echo   LIVE TEST - Enhanced AI Grader
echo ========================================
echo.
echo Starting test in 2 seconds...
timeout /t 2 /nobreak >nul
echo.

python TEST_AI_GRADER.py

echo.
echo ========================================
echo Press any key to exit...
pause >nul
