#!/usr/bin/env python3
import re

print("Reading main.py...")
with open('d:/Morning_Quiz-master/backend/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

print("Fixing syntax errors...")

# Fix the malformed return statement with backticks
content = content.replace(
    'return {`n            "score": round(score, 2),`n            "total_questions": total_marks,`n            "grading_details": grading_details,`n            "message": "Quiz graded successfully"`n        }',
    '''return {
            "score": round(score, 2),
            "total_questions": total_marks,
            "grading_details": grading_details,
            "message": "Quiz graded successfully"
        }'''
)

# Remove excessive blank lines (more than 2 consecutive)
content = re.sub(r'\n\n\n+', '\n\n', content)

# Add the /report-cheating endpoint if it doesn't exist
if '@app.post("/report-cheating")' not in content:
    # Find the position before startup_event
    startup_pos = content.find('@app.on_event("startup")')
    if startup_pos > 0:
        cheating_endpoint = '''
@app.post("/report-cheating")
def report_cheating(data: Dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Report student cheating attempt to teacher"""
    try:
        quiz_id = data.get('quiz_id')
        warnings = data.get('warnings', 0)
        reason = data.get('reason', 'Unknown')
        
        quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
        if not quiz:
            return {"message": "Quiz not found"}
        
        teacher = db.query(User).filter(User.id == quiz.created_by).first()
        if teacher:
            notification = Notification(
                user_id=teacher.id,
                title=f"⚠️ Cheating Alert: {quiz.title}",
                message=f"{current_user.full_name} was caught attempting to cheat ({warnings} violations). Reason: {reason}. Quiz was auto-submitted.",
                type="cheating_alert"
            )
            db.add(notification)
            db.commit()
        
        return {"message": "Cheating reported to teacher"}
    except Exception as e:
        print(f"Error reporting cheating: {e}")
        return {"message": "Failed to report"}

'''
        content = content[:startup_pos] + cheating_endpoint + content[startup_pos:]
        print("Added /report-cheating endpoint")

print("Writing fixed main.py...")
with open('d:/Morning_Quiz-master/backend/main.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Successfully fixed main.py")
print("Verifying syntax...")

import py_compile
try:
    py_compile.compile('d:/Morning_Quiz-master/backend/main.py', doraise=True)
    print("✅ Syntax is valid!")
except SyntaxError as e:
    print(f"❌ Syntax error still exists: {e}")
    exit(1)
