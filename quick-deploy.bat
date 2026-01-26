@echo off
echo Rebuilding and deploying...
cd frontend
call npm run build
if %errorlevel% equ 0 (
    call npx wrangler pages deploy build --project-name=tsskwizi
    echo.
    echo Done! Test at: https://tsskwizi.pages.dev/teacher
) else (
    echo Build failed!
)
pause
