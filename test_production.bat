@echo off
echo ========================================
echo Testing Production Deployment
echo ========================================
echo.

echo Testing Render Backend...
echo URL: https://tvet-quiz-backend.onrender.com/health
echo.
curl -s https://tvet-quiz-backend.onrender.com/health
echo.
echo.

echo ========================================
echo If you see JSON response above with "status": "healthy", backend is working!
echo.
echo If you see an error or timeout:
echo   1. Login to https://dashboard.render.com
echo   2. Check if service is running
echo   3. Check environment variables are set
echo   4. Review logs for errors
echo.
echo ========================================
echo.

echo Testing Login Endpoint...
curl -X POST https://tvet-quiz-backend.onrender.com/auth/login ^
  -H "Content-Type: application/json" ^
  -d "{\"username\":\"teacher001\",\"password\":\"teacher123\"}"
echo.
echo.

echo ========================================
echo If you see "access_token" above, authentication is working!
echo.
echo Next: Test your Cloudflare Pages frontend
echo Visit: https://tsskwizi.pages.dev (or your Cloudflare URL)
echo Try logging in with: teacher001 / teacher123
echo ========================================
echo.
pause
