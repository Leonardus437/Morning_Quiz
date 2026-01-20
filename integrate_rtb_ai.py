#!/usr/bin/env python3
"""
Integration script to add RTB AI Generator to Morning Quiz system
"""

import os
import shutil

def integrate_rtb_ai():
    """Integrate RTB AI Generator into Morning Quiz system"""
    
    print("=== Integrating RTB AI Generator ===\n")
    
    # 1. Copy RTB files to backend
    backend_dir = "backend"
    if not os.path.exists(backend_dir):
        os.makedirs(backend_dir)
    
    rtb_files = [
        "rtb_ai_generator.py",
        "rtb_api.py"
    ]
    
    for file in rtb_files:
        if os.path.exists(file):
            shutil.copy2(file, os.path.join(backend_dir, file))
            print(f"Copied {file} to backend/")
    
    # 2. Copy web interface to frontend
    frontend_dir = "frontend"
    if not os.path.exists(frontend_dir):
        os.makedirs(frontend_dir)
    
    if os.path.exists("rtb_web_interface.html"):
        shutil.copy2("rtb_web_interface.html", os.path.join(frontend_dir, "rtb_generator.html"))
        print("Copied RTB web interface to frontend/")
    
    # 3. Create integration instructions
    instructions = """
# RTB AI Generator Integration Instructions

## Files Added:
- backend/rtb_ai_generator.py - Core AI generator
- backend/rtb_api.py - FastAPI endpoints  
- frontend/rtb_generator.html - Web interface

## To Use:

### 1. Start RTB API Server:
```bash
cd backend
python rtb_api.py
```
Server will run on http://localhost:8000

### 2. Access Web Interface:
Open http://localhost:8000 in browser

### 3. Generate Templates:
- Fill in teacher details (name, subject, topic, etc.)
- Click "Generate" button
- AI creates 100% RTB-compliant templates
- Download as JSON or print

## API Usage:

### Session Plan:
```python
import requests

data = {
    "template_type": "session_plan",
    "trainer_name": "John Doe",
    "topic": "Database Design",
    "learning_outcome": "Design databases",
    "duration": 45
}

response = requests.post("http://localhost:8000/api/generate", json=data)
template = response.json()["template"]
```

### Scheme of Work:
```python
data = {
    "template_type": "scheme_of_work", 
    "course_title": "Web Development",
    "trainer_name": "Jane Smith",
    "module_code": "WEB301"
}

response = requests.post("http://localhost:8000/api/generate", json=data)
template = response.json()["template"]
```

## Integration with Morning Quiz:
1. Add RTB menu item to main navigation
2. Link to /rtb_generator.html
3. Store generated templates in database
4. Create quizzes from RTB content automatically

The AI generates authentic RTB templates that match the exact format and structure of official RTB documents.
"""
    
    with open("RTB_INTEGRATION_GUIDE.md", "w", encoding="utf-8") as f:
        f.write(instructions)
    
    print("Created integration guide")
    
    print("\n=== RTB AI Integration Complete ===")
    print("\nNext steps:")
    print("1. cd backend && python rtb_api.py")
    print("2. Open http://localhost:8000")
    print("3. Fill teacher details and generate RTB templates")
    print("\nThe AI will create 100% RTB-compliant templates!")

if __name__ == "__main__":
    integrate_rtb_ai()