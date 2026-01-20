#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Migrate database to add missing columns"""

import sqlite3
import sys

db_path = "backend/quiz.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 60)
print("DATABASE MIGRATION")
print("=" * 60)

# Check if columns exist
cursor.execute("PRAGMA table_info(users)")
columns = {row[1] for row in cursor.fetchall()}

print(f"\nCurrent columns in users table: {columns}")

# Add missing columns
migrations = [
    ("department", "TEXT", "Adding department column..."),
    ("level", "TEXT", "Adding level column..."),
    ("departments", "JSON", "Adding departments column..."),
    ("password_hash", "TEXT", "Adding password_hash column..."),
    ("is_class_teacher", "BOOLEAN", "Adding is_class_teacher column..."),
]

for col_name, col_type, msg in migrations:
    if col_name not in columns:
        print(f"\n{msg}")
        try:
            cursor.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}")
            print(f"[OK] Added {col_name}")
        except Exception as e:
            print(f"[ERROR] Error adding {col_name}: {e}")
    else:
        print(f"\n[OK] {col_name} already exists")

# Migrate password to password_hash if needed
if "password_hash" in columns and "password" in columns:
    print("\nMigrating password to password_hash...")
    try:
        cursor.execute("UPDATE users SET password_hash = password WHERE password_hash IS NULL")
        print("[OK] Password migration complete")
    except Exception as e:
        print(f"[ERROR] Error: {e}")

conn.commit()

# Verify
print("\n" + "=" * 60)
print("VERIFICATION")
print("=" * 60)

cursor.execute("PRAGMA table_info(users)")
new_columns = {row[1] for row in cursor.fetchall()}
print(f"\nNew columns in users table: {new_columns}")

# Check students
cursor.execute("SELECT COUNT(*) FROM users WHERE role='student'")
student_count = cursor.fetchone()[0]
print(f"\nTotal students: {student_count}")

if student_count > 0:
    cursor.execute("SELECT username, department, level FROM users WHERE role='student' LIMIT 5")
    print("\nSample students:")
    for username, dept, level in cursor.fetchall():
        print(f"  {username}: {dept} - {level}")

conn.close()

print("\n[OK] Migration complete!")
print("\nNext steps:")
print("1. Restart the backend: docker-compose restart backend")
print("2. Upload students with department/level assignments")
print("3. Create a quiz for that department/level")
print("4. Broadcast the quiz")
