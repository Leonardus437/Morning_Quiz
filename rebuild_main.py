import re

with open('d:/Morning_Quiz-master/backend/main.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

clean_lines = []
skip_mode = False
brace_stack = []

for i, line in enumerate(lines):
    stripped = line.strip()
    
    # Skip merge conflict markers
    if stripped.startswith('<<<<<<< HEAD') or stripped.startswith('=======') or stripped.startswith('>>>>>>>'):
        continue
    
    # Track braces to detect incomplete structures
    for char in line:
        if char == '{':
            brace_stack.append(i)
        elif char == '}' and brace_stack:
            brace_stack.pop()
    
    # Skip duplicate function definitions
    if stripped.startswith('def ') or stripped.startswith('@app.'):
        func_sig = stripped.split('(')[0] if '(' in stripped else stripped
        # Check if we already have this function
        recent_content = ''.join(clean_lines[max(0, len(clean_lines)-100):])
        func_exists = func_sig in recent_content
        if func_exists and 'report_cheating' not in func_sig:
            skip_mode = True
            continue
        else:
            skip_mode = False
    
    if skip_mode:
        # Check if we're at the next function
        if (stripped.startswith('def ') or stripped.startswith('@app.')) and i > 0:
            skip_mode = False
        else:
            continue
    
    # Skip lines that create duplicate dict keys in same return statement
    if '"version":' in line and any('"version":' in cl for cl in clean_lines[-10:]):
        continue
    if '"cors":' in line and any('"cors":' in cl for cl in clean_lines[-5:]):
        continue
    if '"fix_deployed":' in line and any('"fix_deployed":' in cl for cl in clean_lines[-5:]):
        continue
    
    # Skip duplicate results.append
    if 'results.append({' in line and any('results.append({' in cl for cl in clean_lines[-20:]):
        # Check if previous append is closed
        if brace_stack:
            continue
    
    clean_lines.append(line)

# Join and write
content = ''.join(clean_lines)

# Remove excessive blank lines
content = re.sub(r'\n\n\n+', '\n\n', content)

# Add anti-cheating endpoint before startup if missing
if '@app.post("/report-cheating")' not in content:
    endpoint = '''
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
    content = content.replace('@app.on_event("startup")', endpoint + '@app.on_event("startup")')

with open('d:/Morning_Quiz-master/backend/main.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Rebuilt main.py")

# Verify syntax
import py_compile
try:
    py_compile.compile('d:/Morning_Quiz-master/backend/main.py', doraise=True)
    print("SUCCESS: Syntax is valid")
except SyntaxError as e:
    print(f"ERROR at line {e.lineno}: {e.msg}")
    with open('d:/Morning_Quiz-master/backend/main.py', 'r') as f:
        lines = f.readlines()
        start = max(0, e.lineno - 5)
        end = min(len(lines), e.lineno + 5)
        print("Context:")
        for i in range(start, end):
            marker = ">>>" if i == e.lineno - 1 else "   "
            print(f"{marker} {i+1}: {lines[i].rstrip()}")
