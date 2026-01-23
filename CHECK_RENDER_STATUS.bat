@echo off
echo Checking Render backend status...
echo.
curl -s https://tvet-quiz-backend.onrender.com/health
echo.
echo.
echo If you see "healthy" above, backend is running.
echo.
echo Next steps:
echo 1. Go to: https://dashboard.render.com/web/srv-d5drg0p5pdvs73dgmbe0
echo 2. Click "Logs" tab
echo 3. Look for errors (especially database errors)
echo 4. Check if it says "Deploy live for ee20511"
echo.
pause
