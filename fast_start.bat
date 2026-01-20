@echo off
echo FAST START - No Docker Build Wait!
echo.
echo Starting Backend directly...
cd backend
start "Backend" python main.py
timeout /t 3
cd ..
echo.
echo Starting Frontend directly...
cd frontend  
start "Frontend" npm run dev -- --host 0.0.0.0 --port 3000
echo.
echo System starting at http://localhost:3000
echo Backend at http://localhost:8000
echo.
pause