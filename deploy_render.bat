@echo off
echo Triggering Render Backend Deployment...
echo.
echo Render will auto-deploy when you push to Git.
echo.
echo Manual deployment steps:
echo 1. Go to https://dashboard.render.com
echo 2. Select "tsskwizi-backend" service
echo 3. Click "Manual Deploy" > "Deploy latest commit"
echo.
echo OR push to Git to trigger auto-deploy:
git add .
git commit -m "Deploy: Latest version"
git push origin main
echo.
pause
