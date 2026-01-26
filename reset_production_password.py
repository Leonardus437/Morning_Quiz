"""
Reset Teacher Password on Render Production Database
Uses the production API to reset password
"""

import requests
import json

RENDER_API = "https://tvet-quiz-backend.onrender.com"

def login_as_admin():
    """Login as admin to get token"""
    print("Logging in as admin...")
    
    try:
        response = requests.post(
            f"{RENDER_API}/auth/login",
            json={"username": "admin", "password": "admin123"},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            print("✅ Admin login successful")
            return token
        else:
            print(f"❌ Admin login failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return None

def get_all_teachers(token):
    """Get all teachers from production"""
    print("\nFetching teachers from production...")
    
    try:
        response = requests.get(
            f"{RENDER_API}/teachers",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
        )
        
        if response.status_code == 200:
            teachers = response.json()
            print(f"✅ Found {len(teachers)} teacher(s) on production:")
            print()
            for i, teacher in enumerate(teachers, 1):
                print(f"{i}. ID: {teacher['id']}")
                print(f"   Username: {teacher['username']}")
                print(f"   Full Name: {teacher['full_name']}")
                print(f"   Departments: {teacher.get('departments', [])}")
                print()
            return teachers
        else:
            print(f"❌ Failed to fetch teachers: {response.text}")
            return []
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def reset_teacher_password_api(token, teacher_id, new_password):
    """Reset teacher password via API"""
    print(f"\nResetting password for teacher ID {teacher_id}...")
    
    try:
        response = requests.post(
            f"{RENDER_API}/admin/reset-teacher-password/{teacher_id}",
            params={"new_password": new_password},
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
        )
        
        if response.status_code == 200:
            print("✅ Password reset successful!")
            print(f"   New password: {new_password}")
            return True
        else:
            print(f"❌ Password reset failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_login(username, password):
    """Test if login works with new password"""
    print(f"\nTesting login for {username}...")
    
    try:
        response = requests.post(
            f"{RENDER_API}/auth/login",
            json={"username": username, "password": password},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ LOGIN SUCCESSFUL!")
            print(f"   User: {data.get('user', {}).get('full_name')}")
            print(f"   Role: {data.get('user', {}).get('role')}")
            return True
        else:
            print(f"❌ LOGIN FAILED: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 70)
    print("RESET TEACHER PASSWORD ON RENDER PRODUCTION")
    print("=" * 70)
    print()
    
    # Step 1: Login as admin
    token = login_as_admin()
    if not token:
        print("\n❌ Cannot proceed without admin access")
        input("\nPress Enter to exit...")
        exit(1)
    
    # Step 2: Get all teachers
    teachers = get_all_teachers(token)
    if not teachers:
        print("\n❌ No teachers found")
        input("\nPress Enter to exit...")
        exit(1)
    
    # Step 3: Select teacher
    print("=" * 70)
    teacher_username = input("\nEnter teacher username to reset (e.g., UWAMARIYA): ").strip()
    
    # Find teacher
    teacher = None
    for t in teachers:
        if t['username'].upper() == teacher_username.upper():
            teacher = t
            break
    
    if not teacher:
        print(f"\n❌ Teacher '{teacher_username}' not found")
        print("\nAvailable teachers:")
        for t in teachers:
            print(f"  - {t['username']}")
        input("\nPress Enter to exit...")
        exit(1)
    
    print(f"\n✅ Found teacher:")
    print(f"   ID: {teacher['id']}")
    print(f"   Username: {teacher['username']}")
    print(f"   Full Name: {teacher['full_name']}")
    
    # Step 4: Get new password
    new_password = input("\nEnter new password: ").strip()
    if not new_password:
        print("\n❌ Password cannot be empty")
        input("\nPress Enter to exit...")
        exit(1)
    
    # Step 5: Confirm
    print("\n" + "=" * 70)
    print("CONFIRMATION")
    print("=" * 70)
    print(f"Teacher: {teacher['username']} ({teacher['full_name']})")
    print(f"New Password: {new_password}")
    print()
    
    confirm = input("Reset password? (yes/no): ").strip().lower()
    
    if confirm != "yes":
        print("\n❌ Cancelled")
        input("\nPress Enter to exit...")
        exit(0)
    
    # Step 6: Reset password
    success = reset_teacher_password_api(token, teacher['id'], new_password)
    
    if success:
        # Step 7: Test login
        print("\n" + "=" * 70)
        print("TESTING NEW PASSWORD")
        print("=" * 70)
        test_login(teacher['username'], new_password)
        
        print("\n" + "=" * 70)
        print("✅ PASSWORD RESET COMPLETE!")
        print("=" * 70)
        print(f"\nYou can now login at: https://tsskwizi.pages.dev/teacher")
        print(f"Username: {teacher['username']}")
        print(f"Password: {new_password}")
    else:
        print("\n❌ Password reset failed")
    
    print()
    input("Press Enter to exit...")
