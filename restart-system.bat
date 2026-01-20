@echo off
echo 🔄 Restarting Morning Quiz System...
echo ================================

echo 📦 Stopping existing containers...
docker-compose down

echo 🧹 Cleaning up...
docker system prune -f

echo 🚀 Starting system with fresh build...
docker-compose up --build -d

echo ⏳ Waiting for services to start...
timeout /t 10 /nobreak > nul

echo 🌐 System URLs:
echo - Student Portal: http://localhost:3000
echo - Teacher Portal: http://localhost:3000/teacher  
echo - DOS Admin Panel: http://localhost:3000/admin
echo.
echo 🔑 Default Admin Credentials:
echo - Username: admin
echo - Password: admin123
echo.
echo ✅ System restart complete!
pause