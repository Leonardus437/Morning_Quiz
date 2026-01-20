@echo off
echo ========================================
echo API ENDPOINT TESTING
echo ========================================
echo.

echo Testing backend health endpoint...
curl -s http://localhost:8000/health
echo.
echo.

echo Testing if backend accepts requests...
curl -s -X GET http://localhost:8000/lessons -H "Content-Type: application/json"
echo.
echo.

echo ========================================
echo API TEST COMPLETE
echo ========================================
echo.
echo If you see JSON responses above, the API is working!
echo.
pause
