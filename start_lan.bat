@echo off
echo Starting Morning Quiz System for LAN Access...

REM Get PC IP address
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr "IPv4"') do set IP=%%a
set IP=%IP: =%

echo Your PC IP: %IP%
echo Students will access: http://%IP%:3000

REM Start system
docker-compose -f docker-compose.offline.yml up -d

echo System started! Share this URL with students:
echo http://%IP%:3000
pause