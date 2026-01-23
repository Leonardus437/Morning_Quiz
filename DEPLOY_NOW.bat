@echo off
color 0A
echo.
echo ========================================
echo   DEPLOY TO PRODUCTION
echo ========================================
echo.
echo Backend: https://tvet-quiz-backend.onrender.com
echo Frontend: https://tsskwizi.pages.dev
echo.
echo [1/4] Building frontend...
cd frontend
call npm install
call npm run build
echo.
echo [2/4] Frontend built successfully!
echo.
echo [3/4] Push backend to GitHub...
cd ..
git add backend/main.py
git commit -m "Update CORS for production"
git push origin main
echo.
echo [4/4] Deploy frontend to Cloudflare...
cd frontend
npx wrangler pages deploy build --project-name=tsskwizi
echo.
echo ========================================
echo   DEPLOYMENT COMPLETE!
echo ========================================
echo.
echo Visit: https://tsskwizi.pages.dev
echo Backend: https://tvet-quiz-backend.onrender.com/health
echo.
pause
