@echo off
echo ========================================
echo FIXING PASSWORD AUTHENTICATION ISSUE
echo ========================================
echo.

cd /d "f:\SIDE HUSTLE\Morning_Quiz"

echo [1] Resetting all user passwords to 'pass123'...

docker-compose exec -T backend python -c "
import bcrypt
import psycopg2
import sys

try:
    # Generate correct hash for pass123
    password = 'pass123'
    correct_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    print(f'Generated hash: {correct_hash[:30]}...')
    
    # Connect to database
    conn = psycopg2.connect('postgresql://quiz_user:quiz_pass123@db:5432/morning_quiz')
    cursor = conn.cursor()
    
    # Update ALL users with the new hash
    cursor.execute('UPDATE users SET password_hash = %s', (correct_hash,))
    rows_updated = cursor.rowcount
    conn.commit()
    
    print(f'✅ Updated {rows_updated} users successfully')
    
    # Test the hash works
    test_result = bcrypt.checkpw(password.encode('utf-8'), correct_hash.encode('utf-8'))
    print(f'✅ Hash verification test: {test_result}')
    
    # List all users
    cursor.execute('SELECT username, role FROM users ORDER BY role, username')
    users = cursor.fetchall()
    print(f'✅ Users in database ({len(users)} total):')
    for username, role in users:
        print(f'   - {username} ({role}) -> password: pass123')
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f'❌ Error: {e}')
    sys.exit(1)
"

if %errorLevel% neq 0 (
    echo ❌ Password update failed!
    pause
    exit /b 1
)

echo.
echo [2] Restarting backend to apply changes...
docker-compose restart backend

echo.
echo [3] Waiting for backend to restart...
ping -n 10 127.0.0.1 >nul

echo.
echo [4] Testing login...
curl -X POST http://localhost:8000/auth/login -H "Content-Type: application/json" -d "{\"username\":\"admin\",\"password\":\"pass123\"}" 2>nul | find "access_token" >nul

if %errorLevel% == 0 (
    echo ✅ Login test SUCCESSFUL!
) else (
    echo ⚠️  Login test failed, but passwords have been reset
)

echo.
echo ========================================
echo 🎉 PASSWORD FIX COMPLETE!
echo ========================================
echo.
echo All users now have password: pass123
echo.
echo 🔑 LOGIN CREDENTIALS:
echo • Admin:    admin / pass123
echo • Teachers: teacher001, teacher002, teacher003 / pass123
echo • Students: student001 to student008 / pass123
echo.
echo 🌐 ACCESS URLS:
echo • Students: http://localhost:3000
echo • Teachers: http://localhost:3000/teacher
echo • Admin:    http://localhost:3000/admin
echo.
echo Press any key to continue...
pause >nul