@echo off
echo Checking TVET Quiz System Status...
echo.
echo Docker containers:
docker ps
echo.
echo Checking ports:
netstat -an | findstr :3000
netstat -an | findstr :8000
echo.
echo If containers are running, access:
echo - System: http://localhost:3000
echo - Admin: http://localhost:3000/admin
echo - Teacher: http://localhost:3000/teacher
echo.
pause