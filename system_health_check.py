import requests
import json

BASE_URL = "http://localhost:8000"

print("=" * 60)
print("🔍 TVET QUIZ SYSTEM - COMPREHENSIVE HEALTH CHECK")
print("=" * 60)

# 1. Health Check
print("\n1️⃣ Testing API Health...")
try:
    response = requests.get(f"{BASE_URL}/health")
    if response.status_code == 200:
        print("   ✅ API is healthy and responding")
    else:
        print(f"   ❌ API health check failed: {response.status_code}")
except Exception as e:
    print(f"   ❌ Cannot connect to API: {e}")

# 2. Admin Login
print("\n2️⃣ Testing Admin Login...")
try:
    response = requests.post(f"{BASE_URL}/auth/login", json={"username": "admin", "password": "pass123"})
    if response.status_code == 200:
        data = response.json()
        admin_token = data.get("access_token")
        print("   ✅ Admin login successful")
        print(f"   👤 User: {data.get('user', {}).get('full_name')}")
        print(f"   🔑 Role: {data.get('user', {}).get('role')}")
    else:
        print(f"   ❌ Admin login failed: {response.json()}")
        admin_token = None
except Exception as e:
    print(f"   ❌ Admin login error: {e}")
    admin_token = None

# 3. Teacher Login
print("\n3️⃣ Testing Teacher Login...")
try:
    response = requests.post(f"{BASE_URL}/auth/login", json={"username": "teacher001", "password": "pass123"})
    if response.status_code == 200:
        data = response.json()
        teacher_token = data.get("access_token")
        print("   ✅ Teacher login successful")
        print(f"   👤 User: {data.get('user', {}).get('full_name')}")
    else:
        print(f"   ❌ Teacher login failed: {response.json()}")
        teacher_token = None
except Exception as e:
    print(f"   ❌ Teacher login error: {e}")
    teacher_token = None

# 4. Student Login
print("\n4️⃣ Testing Student Login...")
try:
    response = requests.post(f"{BASE_URL}/auth/login", json={"username": "student001", "password": "pass123"})
    if response.status_code == 200:
        data = response.json()
        student_token = data.get("access_token")
        print("   ✅ Student login successful")
        print(f"   👤 User: {data.get('user', {}).get('full_name')}")
    else:
        print(f"   ❌ Student login failed: {response.json()}")
        student_token = None
except Exception as e:
    print(f"   ❌ Student login error: {e}")
    student_token = None

# 5. Check Lessons (Admin)
if admin_token:
    print("\n5️⃣ Testing Lessons Management...")
    try:
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/lessons", headers=headers)
        if response.status_code == 200:
            lessons = response.json()
            print(f"   ✅ Lessons endpoint working ({len(lessons)} lessons)")
        else:
            print(f"   ❌ Lessons endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Lessons error: {e}")

# 6. Check Teachers (Admin)
if admin_token:
    print("\n6️⃣ Testing Teachers Management...")
    try:
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/teachers", headers=headers)
        if response.status_code == 200:
            teachers = response.json()
            print(f"   ✅ Teachers endpoint working ({len(teachers)} teachers)")
        else:
            print(f"   ❌ Teachers endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Teachers error: {e}")

# 7. Check Students (Admin)
if admin_token:
    print("\n7️⃣ Testing Students Management...")
    try:
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/admin/students", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Students endpoint working ({data.get('total', 0)} students)")
        else:
            print(f"   ❌ Students endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Students error: {e}")

# 8. Check Questions (Teacher)
if teacher_token:
    print("\n8️⃣ Testing Questions Management...")
    try:
        headers = {"Authorization": f"Bearer {teacher_token}"}
        response = requests.get(f"{BASE_URL}/questions", headers=headers)
        if response.status_code == 200:
            questions = response.json()
            print(f"   ✅ Questions endpoint working ({len(questions)} questions)")
        else:
            print(f"   ❌ Questions endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Questions error: {e}")

# 9. Check Quizzes (Teacher)
if teacher_token:
    print("\n9️⃣ Testing Quizzes Management...")
    try:
        headers = {"Authorization": f"Bearer {teacher_token}"}
        response = requests.get(f"{BASE_URL}/quizzes", headers=headers)
        if response.status_code == 200:
            quizzes = response.json()
            print(f"   ✅ Quizzes endpoint working ({len(quizzes)} quizzes)")
        else:
            print(f"   ❌ Quizzes endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Quizzes error: {e}")

# 10. Check Notifications (Student)
if student_token:
    print("\n🔟 Testing Notifications...")
    try:
        headers = {"Authorization": f"Bearer {student_token}"}
        response = requests.get(f"{BASE_URL}/notifications", headers=headers)
        if response.status_code == 200:
            notifications = response.json()
            print(f"   ✅ Notifications endpoint working ({len(notifications)} notifications)")
        else:
            print(f"   ❌ Notifications endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Notifications error: {e}")

# Summary
print("\n" + "=" * 60)
print("📊 HEALTH CHECK SUMMARY")
print("=" * 60)
print("✅ = Working | ❌ = Issue detected")
print("\nKey Features:")
print("  • API Health Check")
print("  • Admin/Teacher/Student Authentication")
print("  • Lessons Management")
print("  • Teachers Management")
print("  • Students Management")
print("  • Questions Management")
print("  • Quizzes Management")
print("  • Notifications System")
print("\n💡 Check the results above for any ❌ marks")
print("=" * 60)
