#!/usr/bin/env python3
"""
Test script to verify download functionality works
"""
import requests
import json

# Test configuration
BASE_URL = "http://localhost:8000"
ADMIN_CREDENTIALS = {"username": "admin", "password": "admin123"}

def test_downloads():
    print("🧪 Testing Download Functionality...")
    
    # Login as admin
    print("1. Logging in as admin...")
    login_response = requests.post(f"{BASE_URL}/auth/login", json=ADMIN_CREDENTIALS)
    
    if login_response.status_code != 200:
        print("❌ Login failed!")
        return False
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    print("✅ Login successful!")
    
    # Test Excel download
    print("2. Testing Excel download...")
    excel_response = requests.get(f"{BASE_URL}/admin/results/download/excel", headers=headers)
    
    if excel_response.status_code == 200:
        print("✅ Excel download endpoint working!")
        print(f"   Content-Type: {excel_response.headers.get('content-type')}")
        print(f"   Content-Length: {len(excel_response.content)} bytes")
    else:
        print(f"❌ Excel download failed: {excel_response.status_code}")
        print(f"   Error: {excel_response.text}")
    
    # Test PDF download
    print("3. Testing PDF download...")
    pdf_response = requests.get(f"{BASE_URL}/admin/results/download/pdf", headers=headers)
    
    if pdf_response.status_code == 200:
        print("✅ PDF download endpoint working!")
        print(f"   Content-Type: {pdf_response.headers.get('content-type')}")
        print(f"   Content-Length: {len(pdf_response.content)} bytes")
    else:
        print(f"❌ PDF download failed: {pdf_response.status_code}")
        print(f"   Error: {pdf_response.text}")
    
    print("\n🎉 Download functionality test completed!")
    return True

if __name__ == "__main__":
    try:
        test_downloads()
    except Exception as e:
        print(f"❌ Test failed with error: {e}")