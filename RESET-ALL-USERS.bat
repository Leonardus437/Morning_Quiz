@echo off
echo ========================================
echo COMPLETE USER RESET - BRAND NEW USERS
echo ========================================
echo.

cd /d "f:\SIDE HUSTLE\Morning_Quiz"

echo [1] Starting fresh database...
docker-compose up -d db

echo.
echo [2] Waiting for database to initialize...
ping -n 20 127.0.0.1 >nul

echo.
echo [3] Creating brand new users with fresh passwords...
docker-compose exec -T db psql -U quiz_user -d morning_quiz -c "
-- Drop all existing tables
DROP TABLE IF EXISTS quiz_attempts, quiz_questions, quizzes, questions, users CASCADE;

-- Create fresh users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'student',
    full_name VARCHAR(100),
    department VARCHAR(100),
    level VARCHAR(20),
    departments JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"

echo.
echo [4] Starting backend to generate fresh password hashes...
docker-compose up -d backend

echo.
echo [5] Waiting for backend to start...
ping -n 15 127.0.0.1 >nul

echo.
echo [6] Creating brand new users with working passwords...
docker-compose exec -T backend python -c "
import bcrypt
import psycopg2

# Generate fresh hash for 'pass123'
password = 'pass123'
hash_obj = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
password_hash = hash_obj.decode('utf-8')

# Test hash works
test = bcrypt.checkpw(password.encode('utf-8'), hash_obj)
print(f'Password hash test: {test}')

if not test:
    print('ERROR: Hash failed test!')
    exit(1)

# Connect to database
conn = psycopg2.connect('postgresql://quiz_user:quiz_pass123@db:5432/morning_quiz')
cursor = conn.cursor()

# Create brand new users
users = [
    ('admin', 'admin', 'System Administrator', None, None, '[\"Software Development\", \"Computer System and Architecture\", \"Land Surveying\", \"Building Construction\"]'),
    ('teacher001', 'teacher', 'Teacher One', None, None, '[\"Software Development\", \"Computer System and Architecture\"]'),
    ('teacher002', 'teacher', 'Teacher Two', None, None, '[\"Land Surveying\", \"Building Construction\"]'),
    ('teacher003', 'teacher', 'Teacher Three', None, None, '[\"Computer System and Architecture\"]'),
    ('student001', 'student', 'Student One', 'Software Development', 'Level 3', None),
    ('student002', 'student', 'Student Two', 'Computer System and Architecture', 'Level 4', None),
    ('student003', 'student', 'Student Three', 'Computer System and Architecture', 'Level 5', None),
    ('student004', 'student', 'Student Four', 'Land Surveying', 'Level 3', None),
    ('student005', 'student', 'Student Five', 'Building Construction', 'Level 4', None),
    ('student006', 'student', 'Student Six', 'Software Development', 'Level 5', None),
    ('student007', 'student', 'Student Seven', 'Land Surveying', 'Level 5', None),
    ('student008', 'student', 'Student Eight', 'Building Construction', 'Level 5', None)
]

created_count = 0
for username, role, full_name, department, level, departments in users:
    try:
        cursor.execute('''
            INSERT INTO users (username, password_hash, role, full_name, department, level, departments)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (username, password_hash, role, full_name, department, level, departments))
        created_count += 1
        print(f'Created: {username} ({role})')
    except Exception as e:
        print(f'Error creating {username}: {e}')

conn.commit()
cursor.close()
conn.close()

print(f'SUCCESS: Created {created_count} brand new users')
print('All users have password: pass123')
"

if %errorLevel% neq 0 (
    echo ❌ User creation failed!
    pause
    exit /b 1
)

echo.
echo [7] Starting frontend...
docker-compose up -d frontend

echo.
echo [8] Waiting for all services...
ping -n 20 127.0.0.1 >nul

echo.
echo [9] Testing login with brand new users...
curl -X POST http://localhost:8000/auth/login -H "Content-Type: application/json" -d "{\"username\":\"admin\",\"password\":\"pass123\"}" 2>nul | find "access_token" >nul

if %errorLevel% == 0 (
    echo ✅ SUCCESS! Brand new admin login working!
) else (
    echo ❌ Still failing - checking what happened...
    docker-compose logs backend --tail=3
)

echo.
echo Testing teacher login...
curl -X POST http://localhost:8000/auth/login -H "Content-Type: application/json" -d "{\"username\":\"teacher001\",\"password\":\"pass123\"}" 2>nul | find "access_token" >nul

if %errorLevel% == 0 (
    echo ✅ SUCCESS! Teacher login working!
) else (
    echo ❌ Teacher login failed
)

echo.
echo Testing student login...
curl -X POST http://localhost:8000/auth/login -H "Content-Type: application/json" -d "{\"username\":\"student001\",\"password\":\"pass123\"}" 2>nul | find "access_token" >nul

if %errorLevel% == 0 (
    echo ✅ SUCCESS! Student login working!
) else (
    echo ❌ Student login failed
)

echo.
echo ========================================
echo 🎉 BRAND NEW USERS CREATED!
echo ========================================
echo.
echo 🔑 ALL PASSWORDS: pass123
echo.
echo 👨💼 ADMIN: admin / pass123
echo 👩🏫 TEACHERS: teacher001, teacher002, teacher003 / pass123
echo 👨🎓 STUDENTS: student001 to student008 / pass123
echo.
echo 🌐 ACCESS:
echo • http://localhost:3000 (students)
echo • http://localhost:3000/teacher (teachers)
echo • http://localhost:3000/admin (admin)
echo.
echo Press any key to continue...
pause >nul