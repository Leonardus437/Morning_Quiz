@echo off
echo ========================================
echo Creating Test Questions...
echo ========================================
echo.
echo Make sure backend is running first!
echo (Run 1_START_BACKEND.bat in another window)
echo.
timeout /t 3
python test_advanced_questions.py
echo.
echo ========================================
pause
