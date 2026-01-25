@echo off
echo ========================================
echo   Backend Keep-Alive Setup
echo ========================================
echo.

echo Choose your method:
echo.
echo 1. UptimeRobot (Recommended - No coding, 100%% FREE)
echo 2. Deploy Cloudflare Worker (Advanced)
echo 3. Open HTML Monitor Page
echo.

set /p choice="Enter choice (1-3): "

if "%choice%"=="1" (
    echo.
    echo Opening UptimeRobot signup...
    start https://uptimerobot.com/signUp
    echo.
    echo INSTRUCTIONS:
    echo 1. Sign up for FREE account
    echo 2. Click "Add New Monitor"
    echo 3. Set URL: https://tvet-quiz-backend.onrender.com/health
    echo 4. Set Interval: 5 minutes
    echo 5. Click "Create Monitor"
    echo.
    echo Done! Your backend will stay awake 24/7
    pause
)

if "%choice%"=="2" (
    echo.
    echo Deploying Cloudflare Worker...
    npx wrangler deploy keep-alive-worker.js --config wrangler-keepalive.toml
    echo.
    echo Worker deployed! Backend will be pinged every 2 minutes.
    pause
)

if "%choice%"=="3" (
    echo.
    echo Opening HTML Monitor...
    start keep-alive-monitor.html
    echo.
    echo Keep this page open in your browser to monitor backend status.
    echo The page will ping backend every 2 minutes automatically.
    pause
)
