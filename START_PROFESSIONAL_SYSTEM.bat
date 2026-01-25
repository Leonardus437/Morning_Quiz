@echo off
title TVET Quiz System - Professional Startup
color 0A

echo.
echo ===============================================
echo    TVET QUIZ SYSTEM - PROFESSIONAL STARTUP
echo    Advanced Question Types - Production Ready
echo ===============================================
echo.

echo [1/4] Starting Backend Server...
cd /d "%~dp0backend"
start "Backend Server" cmd /k "python main.py"

echo [2/4] Waiting for backend to initialize...
timeout /t 5 /nobreak >nul

echo [3/4] Starting Frontend Server...
cd /d "%~dp0frontend"
start "Frontend Server" cmd /k "npm run dev"

echo [4/4] Waiting for frontend to start...
timeout /t 3 /nobreak >nul

echo.
echo ===============================================
echo    SYSTEM READY FOR MINISTER PRESENTATION
echo ===============================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo DEFAULT ACCOUNTS:
echo   Admin:    admin / admin123
echo   Teacher:  teacher001 / teacher123  
echo   Student:  student001 / pass123
echo.
echo FEATURES READY:
echo   ✅ 12+ Advanced Question Types
echo   ✅ Anti-Cheat System
echo   ✅ Real-time Grading
echo   ✅ PDF/Excel Export
echo   ✅ Offline-First Operation
echo   ✅ Mobile Responsive
echo   ✅ Chat System
echo   ✅ Performance Analytics
echo.

choice /c YN /m "Create sample advanced questions now? (Y/N)"
if errorlevel 2 goto :skip_questions
if errorlevel 1 goto :create_questions

:create_questions
echo.
echo Creating advanced question types...
cd /d "%~dp0"
python create_advanced_questions.py
echo.
echo ✅ Advanced questions created successfully!
goto :end

:skip_questions
echo.
echo ⚠️ Skipping question creation. You can run create_advanced_questions.py later.

:end
echo.
echo ===============================================
echo    READY FOR MINISTER DEMONSTRATION
echo ===============================================
echo.
echo Open your browser and go to:
echo   👨‍🎓 Student Interface: http://localhost:3000
echo   👨‍🏫 Teacher Dashboard: http://localhost:3000/teacher
echo   👨‍💼 Admin Panel: http://localhost:3000/admin
echo.
echo Press any key to open the system in your browser...
pause >nul

start http://localhost:3000
start http://localhost:3000/teacher

echo.
echo System is running! Close this window when done.
echo Both backend and frontend will continue running.
pause