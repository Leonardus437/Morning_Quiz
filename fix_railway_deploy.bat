@echo off
cd /d "%~dp0"
git add nixpacks.toml
git commit -m "Fix Railway auto-deploy: Update to Python 3.11"
git push origin master
echo.
echo Fix pushed! Now reconnect GitHub in Railway dashboard.
echo Railway Dashboard: https://railway.com/project/477122d8-1d79-437f-8513-5bb901527f41/service/ce549504-cde6-4d20-a142-01dc10f54b5f/settings
pause
