@echo off
echo Deploying Backend to Render...
git add backend/
git commit -m "Deploy backend to Render"
git push origin main
echo.
echo Backend pushed to GitHub.
echo Go to https://dashboard.render.com to complete deployment:
echo 1. New Web Service from GitHub repo
echo 2. Root Directory: backend
echo 3. Build: pip install -r requirements.txt
echo 4. Start: uvicorn main:app --host 0.0.0.0 --port $PORT
echo 5. Add DATABASE_URL environment variable
pause
