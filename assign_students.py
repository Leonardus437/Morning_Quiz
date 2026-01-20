#!/usr/bin/env python3
"""Assign department and level to existing students"""

import sqlite3

db_path = "backend/quiz.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 60)
print("ASSIGNING DEPARTMENT/LEVEL TO STUDENTS")
print("=" * 60)

# For Level 3 Computer System and Architecture students
department = "Computer System and Architecture"
level = "Level 3"

print(f"\nAssigning all students to: {department} - {level}")

cursor.execute(
    "UPDATE users SET department = ?, level = ? WHERE role = 'student'",
    (department, level)
)

conn.commit()

# Verify
cursor.execute("SELECT username, department, level FROM users WHERE role='student'")
students = cursor.fetchall()

print(f"\nUpdated {len(students)} students:")
for username, dept, lvl in students:
    print(f"  {username}: {dept} - {lvl}")

conn.close()

print("\n[OK] Assignment complete!")
print("\nNow:")
print("1. Restart backend: docker-compose restart backend")
print("2. Create a quiz for 'Computer System and Architecture' - 'Level 3'")
print("3. Broadcast the quiz - it should now notify all 5 students")
