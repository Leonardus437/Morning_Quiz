@echo off
chcp 65001 >nul
color 0B
title Quick System Test

echo ╔═══════════════════════════════════════╗
echo ║      QUICK SYSTEM TEST                ║
echo ╚═══════════════════════════════════════╝
echo.

echo Testing containers...
docker-compose ps
echo.

echo Testing backend...
curl -s http://localhost:8000/health
echo.

echo Testing frontend...
curl -s -I http://localhost:3000 | findstr "200"
echo.

echo Testing admin login...
curl -s -X POST http://localhost:8000/auth/login -H "Content-Type: application/json" -d "{\"username\":\"admin\",\"password\":\"admin123\"}" | findstr "access_token"
echo.

echo.
echo ✅ Quick test complete!
echo 🌐 Open: http://localhost:3000/admin
echo 🔑 Login: admin / admin123
echo.
pause
