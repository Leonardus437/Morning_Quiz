#!/usr/bin/env python3
"""
Deploy Complete RTB System
"""

import os
import shutil
import json

def deploy_complete_rtb():
    """Deploy complete RTB system to Morning Quiz"""
    
    print("=== Deploying Complete RTB System ===\n")
    
    # Create directories
    os.makedirs("backend", exist_ok=True)
    os.makedirs("frontend", exist_ok=True)
    
    # Copy all RTB files
    rtb_files = {
        "backend": [
            "rtb_complete_generator.py",
            "rtb_scheme_generator.py", 
            "rtb_complete_api.py"
        ],
        "frontend": [
            "rtb_complete_interface.html"
        ]
    }
    
    for directory, files in rtb_files.items():
        for file in files:
            if os.path.exists(file):
                dest_path = os.path.join(directory, file)
                shutil.copy2(file, dest_path)
                print(f"Deployed {file} to {directory}/")
    
    # Create requirements.txt
    requirements = """fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
python-multipart==0.0.6
"""
    
    with open("backend/requirements.txt", "w") as f:
        f.write(requirements)
    print("Created backend/requirements.txt")
    
    # Create startup script
    startup_script = """#!/bin/bash
echo "Starting Complete RTB Generator..."
cd backend
pip install -r requirements.txt
python rtb_complete_api.py
"""
    
    with open("start_rtb.sh", "w") as f:
        f.write(startup_script)
    print("Created start_rtb.sh")
    
    # Create Windows batch file
    batch_script = """@echo off
echo Starting Complete RTB Generator...
cd backend
pip install -r requirements.txt
python rtb_complete_api.py
pause
"""
    
    with open("start_rtb.bat", "w") as f:
        f.write(batch_script)
    print("Created start_rtb.bat")
    
    print("\n=== Complete RTB System Deployed ===")
    print("\nTo start the system:")
    print("Windows: double-click start_rtb.bat")
    print("Linux/Mac: ./start_rtb.sh")
    print("Manual: cd backend && python rtb_complete_api.py")
    print("\nAccess: http://localhost:8000")

if __name__ == "__main__":
    deploy_complete_rtb()