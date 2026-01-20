import sys
sys.path.insert(0, 'backend')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import bcrypt

DATABASE_URL = "sqlite:///backend/quiz.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

db = SessionLocal()

# Hash password using bcrypt
password = "pass123"
salt = bcrypt.gensalt()
password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

# Update admin password
from sqlalchemy import text
result = db.execute(text("UPDATE users SET password_hash = :hash WHERE username = 'admin'"), {"hash": password_hash})
db.commit()

print("SUCCESS: Admin password reset to 'pass123'")
print(f"Rows updated: {result.rowcount}")

# Verify
admin = db.execute(text("SELECT username, role, password_hash FROM users WHERE username = 'admin'")).fetchone()
if admin:
    print(f"Username: {admin[0]}")
    print(f"Role: {admin[1]}")
    print(f"Hash starts with: {admin[2][:20]}...")
    
    # Test password
    test = bcrypt.checkpw(password.encode('utf-8'), admin[2].encode('utf-8'))
    print(f"Password verification test: {'PASS' if test else 'FAIL'}")

db.close()
