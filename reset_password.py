import psycopg2
import bcrypt

conn = psycopg2.connect(
    host='db',
    database='morning_quiz',
    user='quiz_user',
    password='quiz_pass123'
)

cur = conn.cursor()

# Reset teacher001 password
hashed = bcrypt.hashpw('teacher123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
cur.execute("""
    UPDATE users 
    SET password_hash = %s 
    WHERE username = 'teacher001'
""", (hashed,))
conn.commit()

print("✓ Password reset for teacher001")
print("  Username: teacher001")
print("  Password: teacher123")

cur.close()
conn.close()
