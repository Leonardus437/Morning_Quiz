import psycopg2
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

conn = psycopg2.connect(
    host='db',
    database='morning_quiz',
    user='quiz_user',
    password='quiz_pass123'
)

cur = conn.cursor()

# Check if teacher exists
cur.execute("SELECT id, username FROM teachers WHERE username = 'teacher001'")
result = cur.fetchone()

if result:
    print(f"✓ Teacher teacher001 already exists (ID: {result[0]})")
else:
    print("Creating teacher001...")
    hashed = pwd_context.hash('teacher123')
    cur.execute("""
        INSERT INTO teachers (username, password_hash, full_name, email)
        VALUES ('teacher001', %s, 'Default Teacher', 'teacher001@tvet.rw')
    """, (hashed,))
    conn.commit()
    print("✓ Created teacher001 / teacher123")

cur.close()
conn.close()
