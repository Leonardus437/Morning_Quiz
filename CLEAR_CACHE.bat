@echo off
echo Clearing all caches and rebuilding...
cd frontend
rmdir /s /q .svelte-kit 2>nul
rmdir /s /q build 2>nul
rmdir /s /q node_modules\.vite 2>nul
echo Cache cleared!
cd ..
docker-compose down
docker-compose up -d --build
echo Done! Please wait 30 seconds then refresh browser with Ctrl+Shift+R
pause
