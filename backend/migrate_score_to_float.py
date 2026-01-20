"""
Database Migration: Change score column from INTEGER to FLOAT
"""
import psycopg2

# Database connection
conn = psycopg2.connect(
    host="db",
    database="morning_quiz",
    user="quiz_user",
    password="quiz_pass123"
)

cur = conn.cursor()

try:
    # Change score column type
    print("Migrating score column to FLOAT...")
    cur.execute("ALTER TABLE quiz_attempts ALTER COLUMN score TYPE FLOAT USING score::float;")
    conn.commit()
    print("✅ Migration successful!")
except Exception as e:
    print(f"❌ Migration failed: {e}")
    conn.rollback()
finally:
    cur.close()
    conn.close()
