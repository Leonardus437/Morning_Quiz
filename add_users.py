#!/usr/bin/env python3
import sys
sys.path.insert(0, 'backend')

from backend.main import SessionLocal, User, hash_password_simple

db = SessionLocal()

try:
    # Add teacher
    teacher = db.query(User).filter(User.username == "Leonard").first()
    if not teacher:
        teacher = User(
            username="Leonard",
            password_hash=hash_password_simple("12345678"),
            role="teacher",
            full_name="Leonard",
            departments=["Software Development"]
        )
        db.add(teacher)
        print("[+] Teacher Leonard added")
    else:
        print("[*] Teacher Leonard already exists")
    
    # Add student
    student = db.query(User).filter(User.username == "niwemfura1").first()
    if not student:
        student = User(
            username="niwemfura1",
            password_hash=hash_password_simple("student123"),
            role="student",
            full_name="Niwemfura",
            department="Software Development",
            level="Level 5"
        )
        db.add(student)
        print("[+] Student niwemfura1 added")
    else:
        print("[*] Student niwemfura1 already exists")
    
    db.commit()
    print("\n[+] Users added successfully!")
    print("\nLogin credentials:")
    print("Teacher: Leonard / 12345678")
    print("Student: niwemfura1 / student123")
    
except Exception as e:
    print(f"[-] Error: {e}")
    db.rollback()
finally:
    db.close()
