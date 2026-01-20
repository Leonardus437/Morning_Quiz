@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

REM ======================================================
REM Morning Quiz - Full System & Student Upload Automation
REM ======================================================

ECHO.
ECHO ================================================
ECHO   MORNING QUIZ - FULL SYSTEM AUTO VERIFICATION
ECHO ================================================
ECHO.

REM 1) Check Python is available
python --version >NUL 2>&1
IF ERRORLEVEL 1 (
    ECHO [ERROR] Python is not available in PATH.
    ECHO Install Python or add it to PATH, then re-run this script.
    PAUSE
    GOTO :EOF
)

REM 2) Optional: create/activate virtualenv if you use one
IF EXIST venv\Scripts\activate.bat (
    ECHO Activating local virtual environment...
    CALL venv\Scripts\activate.bat
)

REM 3) Run quick system tests
ECHO.
ECHO [1/6] Running core system quick test...
python test_system_simple.py
IF ERRORLEVEL 1 (
    ECHO [WARNING] test_system_simple.py reported issues. Check output above.
)

ECHO.
ECHO [2/6] Checking admin / DOS functionality...
python test_admin_functionality.py
IF ERRORLEVEL 1 (
    ECHO [WARNING] test_admin_functionality.py reported issues. Check output above.
)

ECHO.
ECHO [3/6] Checking teacher basic flow...
python test_teacher_simple.py
IF ERRORLEVEL 1 (
    ECHO [WARNING] test_teacher_simple.py reported issues. Check output above.
)

REM 4) Run student upload flow (using your existing tools)
ECHO.
ECHO [4/6] Running core student upload test...
python test_student_upload.py
IF ERRORLEVEL 1 (
    ECHO [WARNING] test_student_upload.py reported issues. Check output above.
)

ECHO.
ECHO [5/6] Running comprehensive student upload verification...
python test_student_upload_comprehensive.py
IF ERRORLEVEL 1 (
    ECHO [WARNING] test_student_upload_comprehensive.py reported issues. Check output above.
)

ECHO.
ECHO [6/6] Verifying student upload status...
python verify_student_upload.py
IF ERRORLEVEL 1 (
    ECHO [WARNING] verify_student_upload.py reported issues. Check output above.
)

REM 5) Optional: verify RTB integration and offline mode
IF EXIST verify_rtb_integration.py (
    ECHO.
    ECHO [+] Checking RTB integration (optional)...
    python verify_rtb_integration.py
)

IF EXIST verify_offline.bat (
    ECHO.
    ECHO [+] Running offline verification (optional)...
    CALL verify_offline.bat
)

ECHO.
ECHO ================================================
ECHO   MORNING QUIZ - VERIFICATION COMPLETED
ECHO   Review any [WARNING] lines above.
ECHO ================================================
ECHO.
PAUSE
ENDLOCAL
