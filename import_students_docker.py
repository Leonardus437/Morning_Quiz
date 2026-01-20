import pandas as pd
import subprocess
import re

# Read Excel file
df = pd.read_excel('Student list template\\Book1.xlsx', skiprows=4)
df.columns = ['sn', 'name']
df = df[df['name'].notna() & (df['name'] != 'Names')]

# Extract class group
class_df = pd.read_excel('Student list template\\Book1.xlsx', skiprows=1, nrows=1, header=None)
class_group_raw = str(class_df.iloc[0, 0])
if 'Class Group:' in class_group_raw:
    class_group = class_group_raw.replace('Class Group: ', '').strip()
else:
    class_group = 'L5CSA'

print(f"Importing {len(df)} students from {class_group}...")

for idx, row in df.iterrows():
    name = str(row['name']).strip()
    username = re.sub(r'[^a-zA-Z]', '', name.lower())[:15]
    
    # Use Docker exec to insert directly
    sql = f"""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM users WHERE username = '{username}') THEN
            INSERT INTO users (username, password_hash, full_name, role, department, level)
            VALUES ('{username}', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYfj3NnJ/Ry', '{name.replace("'", "''")}', 'student', '{class_group[:3]}', '{class_group}');
        END IF;
    END $$;
    """
    
    result = subprocess.run(
        ['docker', 'exec', '-i', 'morning_quiz-db-1', 'psql', '-U', 'quiz_user', '-d', 'morning_quiz', '-c', sql],
        capture_output=True, text=True
    )
    
    if result.returncode == 0:
        print(f"[OK] {name} -> {username}")
    else:
        print(f"[ERROR] {name}: {result.stderr}")

print("\n[SUCCESS] Import complete! Default password: student123")
