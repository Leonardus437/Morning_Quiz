@echo off
echo ========================================
echo Deploy to Cloudflare and Render
echo ========================================
echo.
echo STEP 1: Install Node.js
echo Download from: https://nodejs.org
echo Install and restart terminal
echo.
echo STEP 2: Build Frontend
echo Run: cd frontend
echo Run: npm install
echo Run: npm run build
echo.
echo STEP 3: Deploy via Git
echo Run: git add .
echo Run: git commit -m "Deploy latest"
echo Run: git push origin main
echo.
echo Both Cloudflare and Render will auto-deploy!
echo.
echo Test after 2-3 minutes:
echo Frontend: https://tsskwizi.pages.dev
echo Backend: https://tvet-quiz-backend.onrender.com/health
echo.
pause
