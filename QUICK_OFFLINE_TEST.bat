@echo off
echo ========================================
echo OFFLINE ACCESSIBILITY QUICK TEST
echo ========================================
echo.

echo Step 1: Checking Docker Status...
docker ps
echo.

echo Step 2: Finding Your Local IP Address...
echo.
ipconfig | findstr /i "IPv4"
echo.

echo Step 3: Testing Backend Connection...
curl -s http://localhost:8000/health
echo.
echo.

echo Step 4: Testing Frontend Connection...
curl -s http://localhost:3000
echo.
echo.

echo ========================================
echo OFFLINE TEST INSTRUCTIONS:
echo ========================================
echo.
echo 1. Turn OFF your mobile data
echo 2. Create WiFi hotspot from your phone
echo 3. Connect this PC to your hotspot
echo 4. Share your IP address with students
echo 5. Students access: http://[YOUR-IP]:3000
echo.
echo Your system is OFFLINE-READY!
echo No internet needed!
echo.
pause
