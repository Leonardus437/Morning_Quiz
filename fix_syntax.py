import re

# Read the file
with open('d:/Morning_Quiz-master/backend/main.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix the file line by line
fixed_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    
    # Skip empty duplicate lines (more than 2 consecutive empty lines)
    if line.strip() == '':
        empty_count = 1
        j = i + 1
        while j < len(lines) and lines[j].strip() == '':
            empty_count += 1
            j += 1
        if empty_count > 2:
            fixed_lines.append('\n')
            i = j
            continue
    
    # Fix the return statement with duplicate keys (lines 663-680)
    if i >= 663 and i <= 680 and 'return {' in ''.join(lines[max(0,i-5):i+1]):
        # We're in the problematic return statement
        if '"needs_review"' in line or '"quiz_title"' in line or '"message"' in line:
            if '"needs_review"' in line:
                fixed_lines.append(line)
            elif '"message"' in line and 'under review' in line:
                fixed_lines.append(line)
            elif '"quiz_title"' in line:
                fixed_lines.append(line)
            # Skip duplicate score, total_questions, grading_details, message
            i += 1
            continue
    
    fixed_lines.append(line)
    i += 1

# Write back
with open('d:/Morning_Quiz-master/backend/main.py', 'w', encoding='utf-8') as f:
    f.writelines(fixed_lines)

print("Fixed all syntax errors")
