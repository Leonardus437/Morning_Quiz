@echo off
echo Deploying Frontend to tsskwizi.pages.dev...
cd frontend
call npm install
call npm run build
call npx wrangler pages deploy build --project-name=tsskwizi
cd ..
echo.
echo Frontend deployed to https://tsskwizi.pages.dev
pause
