#!/usr/bin/env python3
import sys
sys.path.insert(0, '/app')

from main import hash_password_simple, get_db, User

# Create database session
db = next(get_db())

students = [
    {"username": "mugabo", "password": "student123", "full_name": "Jean Paul Mugabo", "department": "Software Development", "level": "Level 5", "school_id": 34, "trade_id": 1},
    {"username": "uwase", "password": "student123", "full_name": "Marie Claire Uwase", "department": "Software Development", "level": "Level 5", "school_id": 34, "trade_id": 1},
    {"username": "niyonzima", "password": "student123", "full_name": "Eric Niyonzima", "department": "Software Development", "level": "Level 5", "school_id": 34, "trade_id": 1}
]

for student_data in students:
    # Check if user already exists
    existing = db.query(User).filter(User.username == student_data["username"]).first()
    if existing:
        print(f"✓ Student {student_data['username']} already exists")
        continue
    
    # Create new student
    password_hash = hash_password_simple(student_data["password"])
    new_student = User(
        username=student_data["username"],
        password_hash=password_hash,
        role="student",
        full_name=student_data["full_name"],
        department=student_data["department"],
        level=student_data["level"],
        school_id=student_data["school_id"],
        trade_id=student_data["trade_id"]
    )
    db.add(new_student)
    print(f"✓ Created student: {student_data['username']} ({student_data['full_name']})")

db.commit()
print("\n✅ All students created successfully!")

# Verify
students_count = db.query(User).filter(User.role == "student").count()
print(f"Total students in database: {students_count}")
