@echo off
echo ========================================
echo STUDENT CREATOR
echo ========================================
echo.
echo This creates 30 students instantly
echo Username: student001 to student030
echo Password: pass123
echo Department: LSV
echo Level: L5
echo.
pause

docker exec tvet_quiz-db-1 psql -U tvetuser -d tvetquiz -c "DO $$ DECLARE i INTEGER; username TEXT; BEGIN FOR i IN 1..30 LOOP username := 'student' || LPAD(i::TEXT, 3, '0'); INSERT INTO users (username, password_hash, full_name, role, department, level) VALUES (username, '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqgOqKqK3i', 'Student ' || i, 'student', 'LSV', 'L5') ON CONFLICT (username) DO NOTHING; END LOOP; END $$; SELECT COUNT(*) as total_students FROM users WHERE role='student';"

echo.
echo ========================================
echo ✅ DONE! Students created
echo ========================================
echo.
echo All students can login with:
echo   Password: pass123
echo.
pause
