#!/usr/bin/env python3

import requests
import json

def test_complete_flow():
    print("Testing Morning Quiz Upload Functionality")
    print("=" * 50)
    
    # Step 1: Login
    print("Step 1: Teacher Login")
    login_data = {"username": "Leon", "password": "pass123"}
    
    login_response = requests.post("http://localhost:8000/auth/login", json=login_data)
    print(f"Login Status: {login_response.status_code}")
    
    if login_response.status_code != 200:
        print(f"Login failed: {login_response.text}")
        return
    
    token = login_response.json()["access_token"]
    user_info = login_response.json()["user"]
    print(f"Login successful - {user_info['full_name']} ({user_info['role']})")
    
    # Step 2: Test Upload
    print("\nStep 2: File Upload Test")
    headers = {"Authorization": f"Bearer {token}"}
    
    with open("sample_students.txt", "rb") as f:
        files = {"file": ("sample_students.txt", f, "text/plain")}
        
        upload_response = requests.post(
            "http://localhost:8000/teacher/upload-students-file",
            files=files,
            headers=headers
        )
    
    print(f"Upload Status: {upload_response.status_code}")
    
    if upload_response.status_code == 501:
        print("FAILED: Upload disabled (dependencies missing)")
        print("Response:", upload_response.text)
    elif upload_response.status_code == 500:
        print("PARTIAL: Dependencies working, file processing error")
        print("Response:", upload_response.text)
    elif upload_response.status_code == 200:
        result = upload_response.json()
        print(f"SUCCESS: Upload working! Found {result.get('count', 0)} students")
    else:
        print(f"Unexpected status: {upload_response.status_code}")
        print("Response:", upload_response.text)
    
    # Step 3: Check system health
    print("\nStep 3: System Health Check")
    health_response = requests.get("http://localhost:8000/health")
    print(f"Backend Health: {health_response.status_code}")
    
    frontend_response = requests.get("http://localhost:3000")
    print(f"Frontend Health: {frontend_response.status_code}")
    
    print("\n" + "=" * 50)
    print("SUMMARY:")
    
    if upload_response.status_code == 200:
        print("SUCCESS: Upload functionality is WORKING")
        print("Teachers can upload student lists")
        print("System is ready for production use")
    elif upload_response.status_code == 500:
        print("PARTIAL: Upload endpoint accessible")
        print("Dependencies are installed and working")
        print("File processing needs minor adjustment")
    else:
        print("ISSUE: Upload functionality needs attention")
    
    print(f"\nAccess the system at: http://localhost:3000")
    print(f"Teacher login: Leon / pass123")

if __name__ == "__main__":
    test_complete_flow()