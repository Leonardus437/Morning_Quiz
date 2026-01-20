@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

ECHO ================================================
ECHO   MORNING QUIZ - FULL AUTO FIX AND VERIFICATION
ECHO ================================================
ECHO.

REM 1) Ensure Python is available
python --version >NUL 2>&1
IF ERRORLEVEL 1 (
    ECHO [ERROR] Python is not available in PATH.
    ECHO Install Python or add it to PATH, then re-run this script.
    PAUSE
    GOTO END_OF_SCRIPT
)

REM 2) Optionally activate venv if present
IF EXIST venv\Scripts\activate.bat (
    ECHO Activating virtual environment...
    CALL venv\Scripts\activate.bat
)

REM 3) Try to update PostgreSQL users column sizes (safe to re-run)
ECHO.
ECHO [DB] Attempting to update users table column sizes in PostgreSQL...
SET PGHOST=localhost
SET PGPORT=5432
SET PGUSER=quiz_user
SET PGPASSWORD=quiz_pass123
SET PGDATABASE=morning_quiz

psql -h %PGHOST% -p %PGPORT% -U %PGUSER% -d %PGDATABASE% -c "ALTER TABLE users ALTER COLUMN username TYPE VARCHAR(50), ALTER COLUMN department TYPE VARCHAR(100), ALTER COLUMN level TYPE VARCHAR(100), ALTER COLUMN full_name TYPE VARCHAR(100);"
IF ERRORLEVEL 1 (
    ECHO [WARNING] Could not run ALTER TABLE automatically.
    ECHO          Make sure PostgreSQL is running and 'psql' is in PATH.
    ECHO          If needed, run this SQL manually in your DB:
    ECHO    ALTER TABLE users ALTER COLUMN username TYPE VARCHAR(50),
    ECHO                     ALTER COLUMN department TYPE VARCHAR(100),
    ECHO                     ALTER COLUMN level TYPE VARCHAR(100),
    ECHO                     ALTER COLUMN full_name TYPE VARCHAR(100);
) ELSE (
    ECHO [OK] users table column sizes updated (or already correct).
)

REM 4) Run the existing full verification script
ECHO.
ECHO [VERIFY] Running full system verification (verify_all_and_upload.bat)...
IF EXIST verify_all_and_upload.bat (
    CALL verify_all_and_upload.bat
) ELSE (
    ECHO [WARNING] verify_all_and_upload.bat not found.
    ECHO           You can run tests manually with:
    ECHO           python test_system_simple.py
    ECHO           python test_admin_functionality.py
    ECHO           python test_teacher_simple.py
    ECHO           python test_student_upload.py
    ECHO           python test_student_upload_comprehensive.py
    ECHO           python verify_student_upload.py
)

ECHO.
ECHO ================================================
ECHO   AUTO FIX AND VERIFICATION SCRIPT COMPLETED
ECHO   Review the output above for any remaining WARNINGS
ECHO ================================================
ECHO.

:END_OF_SCRIPT
PAUSE
ENDLOCAL
EXIT /B 0
