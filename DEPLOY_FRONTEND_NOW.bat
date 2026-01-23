@echo off
color 0A
echo.
echo ========================================
echo   BUILDING AND DEPLOYING FRONTEND
echo ========================================
echo.
cd frontend
echo [1/3] Installing dependencies...
call npm install
echo.
echo [2/3] Building for production...
call npm run build
echo.
echo [3/3] Deploying to Cloudflare...
call npx wrangler pages deploy build --project-name=tsskwizi
echo.
echo ========================================
echo   DEPLOYMENT COMPLETE!
echo ========================================
echo.
echo Visit: https://tsskwizi.pages.dev
echo.
pause
