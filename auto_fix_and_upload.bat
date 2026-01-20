@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

ECHO ================================================
ECHO   MORNING QUIZ - DB FIX + ADMIN EXCEL UPLOAD
ECHO ================================================
ECHO.

REM --- Step 1: PostgreSQL schema fix (prompted) ---
ECHO [DB] Enter PostgreSQL connection details. Press ENTER to accept defaults.
SET /P DB_HOST=Postgres host [localhost]: 
IF "%DB_HOST%"=="" SET DB_HOST=localhost
SET /P DB_PORT=Postgres port [5432]: 
IF "%DB_PORT%"=="" SET DB_PORT=5432
SET /P DB_USER=Postgres user [quiz_user]: 
IF "%DB_USER%"=="" SET DB_USER=quiz_user
SET /P DB_NAME=Database name [morning_quiz]: 
IF "%DB_NAME%"=="" SET DB_NAME=morning_quiz
ECHO (Input will be visible)
SET /P DB_PASS=Postgres password: 
SET PGPASSWORD=%DB_PASS%

ECHO.
ECHO [DB] Applying column size updates on table 'users'...
psql -h %DB_HOST% -p %DB_PORT% -U %DB_USER% -d %DB_NAME% -c "ALTER TABLE users ALTER COLUMN username TYPE VARCHAR(50), ALTER COLUMN department TYPE VARCHAR(100), ALTER COLUMN level TYPE VARCHAR(100), ALTER COLUMN full_name TYPE VARCHAR(100);"
IF ERRORLEVEL 1 (
  ECHO [WARNING] ALTER TABLE failed. Ensure credentials are correct, PostgreSQL is reachable, and psql is installed.
  ECHO          You can apply manually with the same SQL above.
) ELSE (
  ECHO [OK] Database schema updated successfully (or already correct).
)

ECHO.
ECHO -----------------------------------------------
ECHO   BACKEND RESTART RECOMMENDED
ECHO   If your backend is running, restart it now so changes apply.
ECHO   Press any key to continue to Excel upload...
ECHO -----------------------------------------------
PAUSE >NUL

REM --- Step 2: Admin login and Excel upload via API ---
ECHO.
ECHO [API] Provide API details (defaults shown).
SET /P API_BASE=API base [http://localhost:8000]: 
IF "%API_BASE%"=="" SET API_BASE=http://localhost:8000
SET /P ADMIN_USER=Admin username [admin]: 
IF "%ADMIN_USER%"=="" SET ADMIN_USER=admin
ECHO (Input will be visible)
SET /P ADMIN_PASS=Admin password: 

ECHO.
ECHO [API] Logging in to %API_BASE% as %ADMIN_USER% ...
SET TOKEN=
FOR /F "usebackq delims=" %%T IN (`powershell -NoProfile -Command "$r=Invoke-RestMethod -Uri '%API_BASE%/auth/login' -Method Post -ContentType 'application/json' -Body (@{username='%ADMIN_USER%';password='%ADMIN_PASS%'}^|ConvertTo-Json); if($r -and $r.access_token){$r.access_token} else {''}"`) DO SET TOKEN=%%T

IF "%TOKEN%"=="" (
  ECHO [ERROR] Failed to obtain access token. Check API base, username, and password.
  GOTO END_OF_SCRIPT
)
ECHO [OK] Received access token (hidden).

ECHO.
SET /P XLSX_PATH=Full path to .xlsx file to upload (e.g. C:\\Users\\PC\\Downloads\\students.xlsx): 
IF NOT EXIST "%XLSX_PATH%" (
  ECHO [ERROR] File not found: %XLSX_PATH%
  GOTO END_OF_SCRIPT
)

ECHO.
ECHO [UPLOAD] Uploading Excel to %API_BASE%/admin/upload-students-excel ...
curl -s -w "\nHTTP_STATUS: %{http_code}\n" -H "Authorization: Bearer %TOKEN%" -F "file=@%XLSX_PATH%" "%API_BASE%/admin/upload-students-excel"
ECHO.
ECHO If HTTP_STATUS is 200, upload succeeded. Otherwise, review JSON error above.

:END_OF_SCRIPT
ECHO.
ECHO ================================================
ECHO   SCRIPT COMPLETE - REVIEW OUTPUT ABOVE
ECHO ================================================
PAUSE
ENDLOCAL
EXIT /B 0
