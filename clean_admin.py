#!/usr/bin/env python3
import re

# Read the main.py file
with open("backend/main.py", "r", encoding="utf-8") as f:
    content = f.read()

# Remove @reset-admin endpoint
content = re.sub(
    r'@app\.post\("/reset-admin"\).*?return \{"message".*?\}\n',
    '',
    content,
    flags=re.DOTALL
)

# Track removed sections
lines = content.split('\n')
output_lines = []
i = 0

# Patterns of admin endpoints to remove
admin_patterns = [
    r'@app\.post\("/admin/register-teacher"\)',
    r'@app\.get\("/admin/results/download/excel"\)',
    r'@app\.get\("/admin/results/download/pdf"\)',
    r'@app\.post\("/admin/sync-students"\)',
    r'@app\.get\("/admin/students"\)',
    r'@app\.get\("/admin/students/\{student_id\}"\)',
    r'@app\.put\("/admin/students/\{student_id\}"\)',
    r'@app\.delete\("/admin/students/\{student_id\}"\)',
    r'@app\.post\("/admin/assign-class-teacher"\)',
    r'@app\.get\("/admin/class-teachers"\)',
    r'@app\.post\("/admin/upload-students-excel"\)',
    r'@app\.put\("/admin/teacher/\{teacher_id\}"\)',
    r'@app\.post\("/admin/reset-teacher-password/\{teacher_id\}"\)',
    r'@app\.delete\("/admin/clear-all-students"\)',
    r'@app\.get\("/admin/departments"\)',
    r'@app\.get\("/admin/levels"\)',
    r'@app\.get\("/admin/statistics"\)',
    r'@app\.post\("/admin/generate-student-credentials/\{department\}/\{level\}"\)',
    r'@app\.get\("/admin/quiz-reports/\{report_type\}"\)',
    r'@app\.get\("/admin/reports/department"\)',
]

skip_mode = False
skip_depth = 0

while i < len(lines):
    line = lines[i]
    
    # Check if we're starting an admin endpoint
    is_admin_endpoint = False
    for pattern in admin_patterns:
        if re.match(pattern, line.strip()):
            is_admin_endpoint = True
            break
    
    if is_admin_endpoint:
        skip_mode = True
        skip_depth = 1
        i += 1
        # Skip until we hit the next @app decorator at depth 0
        while i < len(lines) and skip_mode:
            current_line = lines[i].strip()
            
            # Count decorator lines
            if current_line.startswith('@'):
                skip_depth -= 1
                if skip_depth == 0:
                    break
            
            i += 1
        skip_mode = False
        continue
    
    # Skip admin initialization code
    if "DOS Administrator" in line or (skip_mode and line.strip() == ""):
        if "DOS Administrator" in line:
            # Skip until next admin field or next section
            i += 1
            while i < len(lines):
                if lines[i].strip() and not lines[i].strip().startswith("#"):
                    if "@app" in lines[i] or "def " in lines[i]:
                        break
                i += 1
            continue
    
    output_lines.append(line)
    i += 1

# Write cleaned content
cleaned_content = '\n'.join(output_lines)

# Replace admin role references with just teacher checks
cleaned_content = re.sub(
    r'if current_user\.role not in \["admin", "teacher"\]',
    'if current_user.role != "teacher"',
    cleaned_content
)

cleaned_content = re.sub(
    r'if current_user\.role in \["admin", "teacher"\]',
    'if current_user.role == "teacher"',
    cleaned_content
)

# Replace admin/DOS specific error messages
cleaned_content = re.sub(
    r'detail="DOS access required"',
    'detail="Teacher access required"',
    cleaned_content
)

with open("backend/main.py", "w", encoding="utf-8") as f:
    f.write(cleaned_content)

print("Cleaned admin code from backend/main.py")
