#!/usr/bin/env python3
"""Fix broadcast issue - Show students and quizzes to match them"""

from main import SessionLocal, User, Quiz

db = SessionLocal()

print("=" * 60)
print("BROADCAST DIAGNOSTIC TOOL")
print("=" * 60)

# Get all students
students = db.query(User).filter(User.role == 'student').all()
print(f"\n✅ Total Students: {len(students)}")

# Group students by department and level
from collections import defaultdict
student_groups = defaultdict(list)
for s in students:
    key = f"{s.department} - {s.level}"
    student_groups[key].append(s.username)

print("\n📊 Students by Department/Level:")
for key, usernames in sorted(student_groups.items()):
    print(f"  {key}: {len(usernames)} students")
    print(f"    Examples: {', '.join(usernames[:5])}")

# Get all quizzes
quizzes = db.query(Quiz).all()
print(f"\n✅ Total Quizzes: {len(quizzes)}")

print("\n📋 Recent Quizzes:")
for q in quizzes[-5:]:
    key = f"{q.department} - {q.level}"
    student_count = len(student_groups.get(key, []))
    status = "✅" if student_count > 0 else "❌"
    print(f"  {status} Quiz {q.id}: {q.title}")
    print(f"     Target: {q.department} - {q.level}")
    print(f"     Matching Students: {student_count}")
    print(f"     Active: {q.is_active}")

print("\n" + "=" * 60)
print("SOLUTION:")
print("=" * 60)
print("\nTo broadcast successfully:")
print("1. Create quiz for: Software Development - Level 4")
print("   (You have 44 students in this group)")
print("\n2. Or upload students matching your quiz department/level")
print("\n3. Check quiz department/level matches student department/level EXACTLY")

db.close()
