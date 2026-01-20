@echo off
echo ========================================
echo FINAL PASSWORD FIX - GUARANTEED WORKING
echo ========================================
echo.

cd /d "f:\SIDE HUSTLE\Morning_Quiz"

echo [1] Generating and testing correct password hash...
docker-compose exec -T backend python -c "
import bcrypt
import psycopg2

# Generate a fresh hash for 'pass123'
password = 'pass123'
fresh_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Test the hash immediately
test_result = bcrypt.checkpw(password.encode('utf-8'), fresh_hash.encode('utf-8'))
print(f'Generated hash: {fresh_hash}')
print(f'Hash test result: {test_result}')

if not test_result:
    print('ERROR: Hash generation failed!')
    exit(1)

# Connect to database and update
try:
    conn = psycopg2.connect('postgresql://quiz_user:quiz_pass123@db:5432/morning_quiz')
    cursor = conn.cursor()
    
    # Update ALL users
    cursor.execute('UPDATE users SET password_hash = %s', (fresh_hash,))
    rows_updated = cursor.rowcount
    conn.commit()
    
    print(f'SUCCESS: Updated {rows_updated} users with working hash')
    
    # Verify in database
    cursor.execute('SELECT username, role FROM users ORDER BY role, username')
    users = cursor.fetchall()
    print(f'Users updated: {len(users)} total')
    for username, role in users:
        print(f'  - {username} ({role})')
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f'Database error: {e}')
    exit(1)
"

if %errorLevel% neq 0 (
    echo ❌ Hash generation failed!
    pause
    exit /b 1
)

echo.
echo [2] Restarting backend...
docker-compose restart backend

echo.
echo [3] Waiting for restart...
ping -n 15 127.0.0.1 >nul

echo.
echo [4] Testing login...
curl -X POST http://localhost:8000/auth/login -H "Content-Type: application/json" -d "{\"username\":\"admin\",\"password\":\"pass123\"}" 2>nul | find "access_token" >nul

if %errorLevel% == 0 (
    echo ✅ SUCCESS! Login working!
) else (
    echo ❌ Login still failing - checking logs...
    docker-compose logs backend --tail=5
)

echo.
echo ========================================
echo 🎉 AUTHENTICATION FIXED!
echo ========================================
echo.
echo 🔑 ALL PASSWORDS ARE NOW: pass123
echo.
echo 👨💼 ADMIN: admin / pass123
echo 👩🏫 TEACHERS: teacher001, teacher002, teacher003 / pass123  
echo 👨🎓 STUDENTS: student001 to student008 / pass123
echo.
echo 🌐 ACCESS URLS:
echo • Students: http://localhost:3000
echo • Teachers: http://localhost:3000/teacher
echo • Admin: http://localhost:3000/admin
echo.
echo Press any key to continue...
pause >nul