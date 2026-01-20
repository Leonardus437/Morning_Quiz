#!/usr/bin/env python3
import re

# Read the file
with open('backend/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the get_questions function
old_pattern = r'@app\.get\("/questions"\)\s*def get_questions\(current_user: User = Depends\(get_current_user\), db: Session = Depends\(get_db\)\):\s*if current_user\.role != "teacher":\s*raise HTTPException\(status_code=403, detail="Teacher or Admin access required"\)\s*# Teachers can only see questions they created\s*if current_user\.role == "teacher":\s*return db\.query\(Question\)\.filter\(Question\.created_by == current_user\.id\)\.all\(\)\s*else:  # admin - can see all\s*return db\.query\(Question\)\.all\(\)'

new_code = '''@app.get("/questions")
def get_questions(
    department: Optional[str] = None,
    level: Optional[str] = None,
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="Teacher or Admin access required")
    
    query = db.query(Question).filter(Question.created_by == current_user.id)
    
    if department:
        query = query.filter(Question.department == department)
    if level:
        query = query.filter(Question.level == level)
    
    return query.all()'''

content = re.sub(old_pattern, new_code, content, flags=re.DOTALL)

# Write back
with open('backend/main.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed get_questions endpoint")
