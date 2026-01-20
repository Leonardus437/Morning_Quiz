@echo off
echo Deploying Frontend to Cloudflare Pages...
cd frontend
call npm install
call npm run build
echo.
echo Build complete! 
echo.
echo Next steps:
echo 1. Go to https://dash.cloudflare.com
echo 2. Select your Pages project (tsskwizi)
echo 3. Go to Settings > Builds & deployments
echo 4. Click "Create deployment"
echo 5. Upload the "frontend/build" folder
echo.
echo OR use Wrangler CLI:
echo npx wrangler pages deploy build --project-name=tsskwizi
echo.
pause
