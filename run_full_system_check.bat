@echo off
setlocal ENABLEDELAYEDEXPANSION

REM ==========================================================
REM  run_full_system_check.bat
REM  - Starts all Docker containers
REM  - Runs backend/system health checks
REM  - Runs admin, teacher and student role tests
REM ==========================================================

echo.
echo ==========================================================
echo   RTB / Morning_Quiz - FULL SYSTEM CHECK
echo ==========================================================
echo.

REM Move to script directory (project root)
cd /d "%~dp0"

REM ----------------------------------------------------------
REM 1. Start Docker containers (main compose file)
REM ----------------------------------------------------------

echo [1/7] Checking Docker availability...
where docker >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not installed or not in PATH.
    goto :END
)

echo.
echo [2/7] Starting Docker containers with docker-compose.yml ...

REM Very simple logic to avoid parser issues: try docker-compose, then docker compose
where docker-compose >nul 2>&1
if not errorlevel 1 (
    echo Using docker-compose...
    docker-compose up -d
    if errorlevel 1 (
        echo ERROR: Failed to start Docker containers with docker-compose.
        goto :END
    )
    goto :AFTER_DOCKER
)

REM Fallback: try docker compose (v2)
where docker >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker CLI not found.
    goto :END
)

echo Using docker compose (v2)...
docker compose up -d
if errorlevel 1 (
    echo ERROR: Failed to start Docker containers with docker compose.
    goto :END
)

:AFTER_DOCKER

echo.
echo Docker containers requested to start. Waiting 10 seconds for services to initialize...
TIMEOUT /T 10 /NOBREAK >nul

REM ----------------------------------------------------------
REM 2. Check backend health
REM ----------------------------------------------------------

echo.
echo [3/7] Checking backend health...

where curl >nul 2>&1
if errorlevel 1 (
    echo ERROR: curl is not installed or not in PATH.
    goto :END
)

curl -f http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    echo ERROR: Backend is not healthy. Run the following commands to diagnose:
    echo   docker-compose logs backend
    echo   docker-compose exec backend bash
    echo   # Then inside container: python -c "import main; print('Import OK')"
    goto :END
)

echo Backend is healthy.

REM ----------------------------------------------------------
REM 3. Basic backend + system health checks
REM ----------------------------------------------------------

echo.
echo [4/7] Running backend and system health checks...

where python >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH.
    goto :END
)

if exist backend_verify.py (
    echo   -> python backend_verify.py
    python backend_verify.py
    if errorlevel 1 echo   WARNING: backend_verify.py reported an error.
) else (
    echo   NOTE: backend_verify.py not found, skipping.
)

if exist system_health_check.py (
    echo   -> python system_health_check.py
    python system_health_check.py
    if errorlevel 1 echo   WARNING: system_health_check.py reported an error.
) else (
    echo   NOTE: system_health_check.py not found, skipping.
)

if exist final_verification.bat (
    echo   -> final_verification.bat
    call final_verification.bat
    if errorlevel 1 echo   WARNING: final_verification.bat reported an error.
) else (
    echo   NOTE: final_verification.bat not found, skipping.
)

REM ----------------------------------------------------------
REM 4. Admin, Teacher, Student flows
REM ----------------------------------------------------------

echo.
echo [5/7] Running core system flow tests...

if exist test_system_simple.py (
    echo   -> python test_system_simple.py
    python test_system_simple.py
    if errorlevel 1 echo   WARNING: test_system_simple.py reported an error.
) else (
    echo   NOTE: test_system_simple.py not found, skipping.
)

echo.
echo [6/7] Running Admin role tests...

if exist test_admin_functionality.py (
    echo   -> python test_admin_functionality.py
    python test_admin_functionality.py
    if errorlevel 1 echo   WARNING: test_admin_functionality.py reported an error.
) else (
    echo   NOTE: test_admin_functionality.py not found, skipping.
)

if exist test_admin.bat (
    echo   -> test_admin.bat
    call test_admin.bat
    if errorlevel 1 echo   WARNING: test_admin.bat reported an error.
) else (
    echo   NOTE: test_admin.bat not found, skipping.
)

if exist test_admin_simple.bat (
    echo   -> test_admin_simple.bat
    call test_admin_simple.bat
    if errorlevel 1 echo   WARNING: test_admin_simple.bat reported an error.
) else (
    echo   NOTE: test_admin_simple.bat not found, skipping.
)


echo.
echo [7/7] Running Teacher and Student role tests...

REM Teacher tests
if exist test_teacher_simple.py (
    echo   -> python test_teacher_simple.py
    python test_teacher_simple.py
    if errorlevel 1 echo   WARNING: test_teacher_simple.py reported an error.
) else (
    echo   NOTE: test_teacher_simple.py not found, skipping.
)

if exist test_lesson_creation.py (
    echo   -> python test_lesson_creation.py
    python test_lesson_creation.py
    if errorlevel 1 echo   WARNING: test_lesson_creation.py reported an error.
) else (
    echo   NOTE: test_lesson_creation.py not found, skipping.
)

if exist test_lesson_assignment.py (
    echo   -> python test_lesson_assignment.py
    python test_lesson_assignment.py
    if errorlevel 1 echo   WARNING: test_lesson_assignment.py reported an error.
) else (
    echo   NOTE: test_lesson_assignment.py not found, skipping.
)

REM Student tests
if exist test_student_upload.py (
    echo   -> python test_student_upload.py
    python test_student_upload.py
    if errorlevel 1 echo   WARNING: test_student_upload.py reported an error.
) else (
    echo   NOTE: test_student_upload.py not found, skipping.
)

if exist test_student_upload_enhanced.py (
    echo   -> python test_student_upload_enhanced.py
    python test_student_upload_enhanced.py
    if errorlevel 1 echo   WARNING: test_student_upload_enhanced.py reported an error.
) else (
    echo   NOTE: test_student_upload_enhanced.py not found, skipping.
)

if exist test_student_upload_comprehensive.py (
    echo   -> python test_student_upload_comprehensive.py
    python test_student_upload_comprehensive.py
    if errorlevel 1 echo   WARNING: test_student_upload_comprehensive.py reported an error.
) else (
    echo   NOTE: test_student_upload_comprehensive.py not found, skipping.
)

REM ----------------------------------------------------------
REM 4. Optional: offline / integration verification (if present)
REM ----------------------------------------------------------

echo.
echo [OPTIONAL] Running integration / offline checks if available...

if exist verify_rtb_integration.py (
    echo   -> python verify_rtb_integration.py
    python verify_rtb_integration.py
    if errorlevel 1 echo   WARNING: verify_rtb_integration.py reported an error.
) else (
    echo   NOTE: verify_rtb_integration.py not found, skipping.
)

if exist verify_offline.bat (
    echo   -> verify_offline.bat
    call verify_offline.bat
    if errorlevel 1 echo   WARNING: verify_offline.bat reported an error.
) else (
    echo   NOTE: verify_offline.bat not found, skipping.
)

:END
echo.
echo ==========================================================
echo   FULL SYSTEM CHECK COMPLETE.
echo   Review any WARNING or ERROR messages above.
echo ==========================================================
echo.
pause
endlocal
