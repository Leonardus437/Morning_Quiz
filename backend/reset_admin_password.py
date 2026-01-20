#!/usr/bin/env python3
"""Reset admin password"""
import sqlite3
import hashlib

def hash_password_simple(password: str) -> str:
    """Simple password hashing"""
    return hashlib.sha256(password.encode()).hexdigest()

# Connect to database
conn = sqlite3.connect('quiz.db')
cursor = conn.cursor()

# Reset admin password to 'admin123'
new_password_hash = hash_password_simple('admin123')
cursor.execute("UPDATE users SET password_hash = ? WHERE username = 'admin'", (new_password_hash,))

# Reset student001 password to 'student123'
student_password_hash = hash_password_simple('student123')
cursor.execute("UPDATE users SET password_hash = ? WHERE username = 'student001'", (student_password_hash,))

conn.commit()
print("✅ Passwords reset successfully!")
print("   admin / admin123")
print("   student001 / student123")
conn.close()
