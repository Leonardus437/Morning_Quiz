@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

ECHO ================================================
ECHO   MORNING QUIZ - DOCKER FIX + VERIFY AUTOMATION
ECHO ================================================
ECHO.

REM Ensure we're in the project directory (contains docker-compose.yml)
IF NOT EXIST docker-compose.yml (
  ECHO [ERROR] docker-compose.yml not found in current directory.
  ECHO Run this script from: c:\Users\PC\Music\Morning_Quiz
  PAUSE
  GOTO END
)

REM 1) Show compose services
ECHO.
ECHO [DOCKER] Current services status:
docker compose ps

REM 2) Apply DB schema fix inside the Postgres container (service name: db)
ECHO.
ECHO [DB] Applying ALTER TABLE in Postgres container 'db'...
docker compose exec -e PGPASSWORD=quiz_pass123 db psql -U quiz_user -d morning_quiz -c "ALTER TABLE users ALTER COLUMN username TYPE VARCHAR(50), ALTER COLUMN department TYPE VARCHAR(100), ALTER COLUMN level TYPE VARCHAR(100), ALTER COLUMN full_name TYPE VARCHAR(100);"
IF ERRORLEVEL 1 (
  ECHO [WARNING] Failed to ALTER TABLE inside container. Verify service name 'db'.
  ECHO           If your DB service name differs, edit this script and change 'db'.
) ELSE (
  ECHO [OK] Database schema updated (or already correct).
)

REM 3) Switch backend to run updated app module (backend_running:app) if needed
ECHO.
ECHO [BACKEND] Checking backend start command. If it runs main:app, we will patch compose file to run backend_running:app.

REM Create a backup of docker-compose.yml
IF NOT EXIST docker-compose.yml.bak (
  COPY /Y docker-compose.yml docker-compose.yml.bak >NUL
)

REM Use PowerShell to replace 'uvicorn main:app' with 'uvicorn backend_running:app'
powershell -NoProfile -Command "(Get-Content 'docker-compose.yml') -replace 'uvicorn\s+main:app', 'uvicorn backend_running:app' | Set-Content 'docker-compose.yml'"
IF ERRORLEVEL 1 (
  ECHO [WARNING] Could not patch docker-compose.yml automatically. Ensure backend runs 'uvicorn backend_running:app'.
) ELSE (
  ECHO [OK] Ensured backend uses backend_running:app (compose file patched if needed). Backup at docker-compose.yml.bak
)

REM 4) Rebuild and restart backend
ECHO.
ECHO [DOCKER] Rebuilding and restarting backend service...
docker compose up -d --build backend
IF ERRORLEVEL 1 (
  ECHO [ERROR] Failed to rebuild/restart backend. Check Docker output above.
  PAUSE
  GOTO END
)

docker compose ps

REM 5) Run full verification
ECHO.
ECHO [VERIFY] Running verify_all_and_upload.bat...
IF EXIST verify_all_and_upload.bat (
  CALL verify_all_and_upload.bat
) ELSE (
  ECHO [WARNING] verify_all_and_upload.bat not found. Skipping.
)

ECHO.
ECHO ================================================
ECHO   DOCKER FIX + VERIFY COMPLETE
ECHO   If Excel upload still fails, use auto_fix_and_upload.bat
ECHO   to upload a known .xlsx directly to the API.
ECHO ================================================
ECHO.
:END
PAUSE
ENDLOCAL
EXIT /B 0
