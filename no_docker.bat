@echo off
echo Starting TVET Quiz System WITHOUT Docker...
echo.
echo Starting Backend...
cd backend
start "Backend" python main.py
cd ..
echo.
echo Starting Frontend...
cd frontend
start "Frontend" npm run dev
cd ..
echo.
echo System starting...
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
echo.
pause