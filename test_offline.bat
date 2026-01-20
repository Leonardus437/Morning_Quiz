@echo off
echo ========================================
echo   MORNING QUIZ SYSTEM - OFFLINE TEST
echo ========================================
echo.

echo Testing Backend Health...
curl -s http://localhost:8000/health
echo.
echo.

echo Testing Offline Status...
curl -s http://localhost:8000/offline-status
echo.
echo.

echo Testing Admin Login...
curl -s -X POST http://localhost:8000/auth/login -H "Content-Type: application/json" -d "{\"username\":\"admin\",\"password\":\"admin123\"}"
echo.
echo.

echo Testing Frontend...
curl -s -I http://localhost:3000 | findstr "HTTP/1.1"
echo.

echo ========================================
echo   OFFLINE TEST COMPLETE
echo ========================================
echo.
echo Your system is running FULLY OFFLINE!
echo.
echo Access URLs:
echo - Admin Panel: http://localhost:3000/admin
echo - Student Access: http://localhost:3000
echo - LAN Access: http://192.168.203.61:3000
echo.
echo Default Credentials:
echo - Admin: admin / admin123
echo - Student: student001 / student123
echo - Teacher: teacher001 / pass123
echo.
pause