
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
