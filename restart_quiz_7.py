import requests
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Login as teacher
login_response = requests.post(
    "http://localhost:8000/auth/login",
    json={"username": "teacher001", "password": "teacher123"}
)

if login_response.status_code == 200:
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    print("[OK] Logged in as teacher001\n")
    
    # Broadcast quiz 7 again to restart timer
    print("[BROADCAST] Restarting Quiz 7...")
    broadcast_response = requests.put(
        "http://localhost:8000/quizzes/7/broadcast",
        headers=headers
    )
    
    print(f"\nStatus Code: {broadcast_response.status_code}")
    
    if broadcast_response.status_code == 200:
        result = broadcast_response.json()
        print(f"\n[SUCCESS] {result.get('message')}")
        print(f"Students Notified: {result.get('students_notified')}")
        print(f"\nQuiz 7 is now LIVE again! Students can now start the quiz.")
    else:
        print(f"\n[ERROR] {broadcast_response.text}")
    
else:
    print(f"[ERROR] Login failed: {login_response.status_code}")
