import re

# Read the file
with open('d:/Morning_Quiz-master/backend/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove all merge conflict markers
content = re.sub(r'<<<<<<< HEAD\r?\n', '', content)
content = re.sub(r'=======\r?\n', '', content)
content = re.sub(r'>>>>>>> .*\r?\n', '', content)

# Fix duplicate completed_at issue (keep only one)
content = re.sub(
    r'completed_at=now\(\),\s*needs_review=True.*?\s*completed_at=now\(\)',
    'completed_at=now()',
    content,
    flags=re.DOTALL
)

# Remove duplicate function definitions
lines = content.split('\n')
seen_functions = set()
cleaned_lines = []
skip_until_next_def = False

for i, line in enumerate(lines):
    # Check if this is a function definition
    if line.strip().startswith('def ') or line.strip().startswith('@app.'):
        func_name = line.strip()
        if func_name in seen_functions:
            skip_until_next_def = True
            continue
        else:
            seen_functions.add(func_name)
            skip_until_next_def = False
    
    if not skip_until_next_def:
        cleaned_lines.append(line)

content = '\n'.join(cleaned_lines)

# Write back
with open('d:/Morning_Quiz-master/backend/main.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed main.py successfully")
