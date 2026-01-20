@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

REM ================================================
REM Update Morning Quiz DB schema and backend checks
REM ================================================

ECHO.
ECHO Updating PostgreSQL users table column sizes...
ECHO This will allow longer department/level names.

REM NOTE: Adjust connection details if different in your environment
SET PGHOST=localhost
SET PGPORT=5432
SET PGUSER=quiz_user
SET PGPASSWORD=quiz_pass123
SET PGDATABASE=morning_quiz

REM Run ALTER TABLE via psql (requires psql installed and in PATH)
psql -h %PGHOST% -p %PGPORT% -U %PGUSER% -d %PGDATABASE% -c "ALTER TABLE users ALTER COLUMN username TYPE VARCHAR(50), ALTER COLUMN department TYPE VARCHAR(100), ALTER COLUMN level TYPE VARCHAR(100), ALTER COLUMN full_name TYPE VARCHAR(100);"

IF ERRORLEVEL 1 (
    ECHO.
    ECHO [WARNING] Failed to run ALTER TABLE. Ensure PostgreSQL is running and 'psql' is in PATH.
    ECHO You may need to apply this SQL manually:
    ECHO   ALTER TABLE users ALTER COLUMN username TYPE VARCHAR(50),^ 
    ECHO                ALTER COLUMN department TYPE VARCHAR(100),^ 
    ECHO                ALTER COLUMN level TYPE VARCHAR(100),^ 
    ECHO                ALTER COLUMN full_name TYPE VARCHAR(100);
) ELSE (
    ECHO.
    ECHO [OK] users table column sizes updated successfully.
)

ECHO.
ECHO Backend Python file (backend_running.py) has already been updated to:
ECHO  - Allow Admin and Teacher on /admin/upload-students-excel
ECHO  - Restrict student upload to Excel files only (.xlsx, .xls)
ECHO  - Keep other behavior unchanged
ECHO.
ECHO Now restart your backend and run:
ECHO   verify_all_and_upload.bat
ECHO to confirm all important checks pass.
ECHO.
PAUSE
ENDLOCAL
