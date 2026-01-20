import requests

BASE_URL = "http://localhost:8000"

print("=" * 70)
print("CLEAR ALL STUDENTS AND RE-UPLOAD")
print("=" * 70)

# Step 1: Login
print("\n1. Logging in as admin...")
login = requests.post(f"{BASE_URL}/auth/login", json={
    "username": "admin",
    "password": "admin123"
})
if login.status_code != 200:
    print(f"ERROR: Login failed - {login.text}")
    exit(1)

token = login.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print("   SUCCESS: Logged in")

# Step 2: Clear all students
print("\n2. Clearing all existing students...")
clear = requests.delete(f"{BASE_URL}/admin/clear-all-students", headers=headers)
if clear.status_code == 200:
    result = clear.json()
    print(f"   SUCCESS: Deleted {result['count']} students")
else:
    print(f"   ERROR: {clear.text}")
    exit(1)

# Step 3: Upload Excel file
print("\n3. Uploading L5 LSV.xls...")
excel_path = "STUDENT LIST EXCEL FILES/L5 LSV.xls"
with open(excel_path, 'rb') as f:
    files = {'file': ('L5 LSV.xls', f, 'application/vnd.ms-excel')}
    data = {'department': 'LSV', 'level': 'L5'}
    upload = requests.post(
        f"{BASE_URL}/admin/upload-students-excel",
        headers=headers,
        files=files,
        data=data
    )

if upload.status_code == 200:
    result = upload.json()
    print(f"   SUCCESS: Uploaded {result['total']} students")
    print(f"   Created: {result['created']}, Updated: {result['updated']}")
else:
    print(f"   ERROR: {upload.text}")
    exit(1)

# Step 4: Verify
print("\n4. Verifying students in database...")
verify = requests.get(f"{BASE_URL}/admin/students", headers=headers)
if verify.status_code == 200:
    students = verify.json()['students']
    lsv_students = [s for s in students if s['department'] == 'LSV' and s['level'] == 'L5']
    print(f"   SUCCESS: Found {len(lsv_students)} L5 LSV students")
    print("\n   First 5 students:")
    for s in lsv_students[:5]:
        print(f"      {s['full_name']:30} | {s['username']}")
else:
    print(f"   ERROR: {verify.text}")

# Step 5: Test login
print("\n5. Testing student login...")
test_login = requests.post(f"{BASE_URL}/auth/login", json={
    "username": "batamuriza1",
    "password": "student123"
})
if test_login.status_code == 200:
    user = test_login.json()['user']
    print(f"   SUCCESS: {user['full_name']} logged in")
else:
    print(f"   ERROR: Login failed - {test_login.text}")

print("\n" + "=" * 70)
print("COMPLETE! All students cleared and re-uploaded successfully")
print("=" * 70)
print("\nCREDENTIALS:")
print("   Admin: admin / admin123")
print("   All Students: [firstname][number] / student123")
print("   Example: batamuriza1 / student123")
print("=" * 70)
