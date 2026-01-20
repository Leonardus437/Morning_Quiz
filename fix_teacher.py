#!/usr/bin/env python3
import sys
sys.path.insert(0, 'backend')

from backend.main import SessionLocal, User

db = SessionLocal()

try:
    teacher = db.query(User).filter(User.username == "Leonard").first()
    if teacher:
        teacher.departments = ["Software Development"]
        db.commit()
        print("[+] Leonard's departments updated to: Software Development")
    else:
        print("[-] Leonard not found")
        
except Exception as e:
    print(f"[-] Error: {e}")
    db.rollback()
finally:
    db.close()
