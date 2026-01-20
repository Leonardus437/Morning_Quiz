import re

with open('d:/Morning_Quiz-master/backend/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix backtick newlines
content = content.replace('`n', '\n')

# Fix duplicate version in health endpoint - keep only the second one
content = re.sub(
    r'"version": "1\.8-SUBMISSION-FIX",\s*"cors": "enabled",\s*"fix_deployed": "2026-01-10-12:40"\s*"version": "2\.0-AI-GRADER-RESTORED",',
    '"version": "2.0-ANTI-CHEAT",',
    content
)

# Remove excessive blank lines
content = re.sub(r'\n\n\n+', '\n\n', content)

# Ensure /report-cheating endpoint exists
if '@app.post("/report-cheating")' not in content:
    startup_marker = '@app.on_event("startup")'
    if startup_marker in content:
        endpoint_code = '''
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
        content = content.replace(startup_marker, endpoint_code + startup_marker)

with open('d:/Morning_Quiz-master/backend/main.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed main.py")
