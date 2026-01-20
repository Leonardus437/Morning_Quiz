#!/usr/bin/env python3
"""Fix students by assigning them to the correct department and level"""

import sqlite3

# Connect to database
conn = sqlite3.connect('backend/quiz.db')
cursor = conn.cursor()

# Check current students
print("Current students:")
cursor.execute("SELECT id, username, full_name, department, level FROM users WHERE role='student'")
for row in cursor.fetchall():
    print(f"  {row}")

# Update all students to match the quiz
print("\nUpdating students to 'Computer System and Architecture' - 'Level 3'...")
cursor.execute("""
    UPDATE users 
    SET department='Computer System and Architecture', level='Level 3'
    WHERE role='student'
""")

conn.commit()

# Verify update
print("\nUpdated students:")
cursor.execute("SELECT id, username, full_name, department, level FROM users WHERE role='student'")
for row in cursor.fetchall():
    print(f"  {row}")

conn.close()
print("\n✅ Done! Students are now assigned to 'Computer System and Architecture' - 'Level 3'")
