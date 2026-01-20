@echo off
setlocal enabledelayedexpansion

echo ========================================
echo SIMPLE STUDENT UPLOAD
echo ========================================
echo.
echo This will create 30 sample students
echo Department: LSV
echo Level: L5
echo.
pause

echo Creating students...

docker exec tvet_quiz-db-1 psql -U tvetuser -d tvetquiz -c "
DO $$
DECLARE
    i INTEGER;
    username TEXT;
    password_hash TEXT;
BEGIN
    FOR i IN 1..30 LOOP
        username := 'student' || LPAD(i::TEXT, 3, '0');
        password_hash := '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqgOqKqK3i'; -- 'pass123'
        
        INSERT INTO users (username, password_hash, full_name, role, department, level, is_active)
        VALUES (
            username,
            password_hash,
            'Student ' || i,
            'student',
            'LSV',
            'L5',
            true
        )
        ON CONFLICT (username) DO NOTHING;
    END LOOP;
END $$;
"

echo.
echo ========================================
echo ✅ Created 30 students!
echo ========================================
echo.
echo Credentials:
echo   Username: student001 to student030
echo   Password: pass123
echo.
echo Students can now login at:
echo   http://localhost:3000
echo.
pause
