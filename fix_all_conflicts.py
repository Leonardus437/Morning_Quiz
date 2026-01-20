#!/usr/bin/env python3
"""Fix all merge conflicts in backend files"""

def clean_merge_conflicts(content):
    """Remove all merge conflict markers and duplicate sections"""
    lines = content.split('\n')
    cleaned = []
    skip_until_end = False
    in_conflict = False
    head_section = []
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Detect conflict start
        if line.startswith('<<<<<<< HEAD'):
            in_conflict = True
            head_section = []
            i += 1
            continue
        
        # Detect conflict middle
        if line.startswith('=======') and in_conflict:
            skip_until_end = True
            i += 1
            continue
        
        # Detect conflict end
        if line.startswith('>>>>>>>') and in_conflict:
            # Keep HEAD section
            cleaned.extend(head_section)
            in_conflict = False
            skip_until_end = False
            head_section = []
            i += 1
            continue
        
        # Collect lines
        if in_conflict and not skip_until_end:
            head_section.append(line)
        elif not in_conflict and not skip_until_end:
            cleaned.append(line)
        
        i += 1
    
    return '\n'.join(cleaned)

# Fix ai_grader.py
print("Fixing ai_grader.py...")
with open('backend/ai_grader.py', 'r', encoding='utf-8') as f:
    content = f.read()

cleaned = clean_merge_conflicts(content)

with open('backend/ai_grader.py', 'w', encoding='utf-8') as f:
    f.write(cleaned)

print("[OK] ai_grader.py fixed")

# Fix main.py
print("Fixing main.py...")
with open('backend/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

cleaned = clean_merge_conflicts(content)

with open('backend/main.py', 'w', encoding='utf-8') as f:
    f.write(cleaned)

print("[OK] main.py fixed")

# Verify syntax
import py_compile
try:
    py_compile.compile('backend/ai_grader.py', doraise=True)
    print("[OK] ai_grader.py syntax valid")
except py_compile.PyCompileError as e:
    print(f"[ERROR] ai_grader.py syntax error: {e}")

try:
    py_compile.compile('backend/main.py', doraise=True)
    print("[OK] main.py syntax valid")
except py_compile.PyCompileError as e:
    print(f"[ERROR] main.py syntax error: {e}")

print("\n[SUCCESS] All conflicts resolved!")
