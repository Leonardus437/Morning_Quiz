import pandas as pd
import psycopg2
import bcrypt
import re

# Database connection
conn = psycopg2.connect(
    host="localhost",
    database="morning_quiz",
    user="quiz_user",
    password="quiz_pass123",
    port="5432"
)
cur = conn.cursor()

# Read Excel file
df = pd.read_excel('Student list template\\Book1.xlsx', skiprows=4)
df.columns = ['sn', 'name']
df = df[df['name'].notna() & (df['name'] != 'Names')]

# Extract class group from file
class_df = pd.read_excel('Student list template\\Book1.xlsx', skiprows=1, nrows=1, header=None)
class_group = str(class_df.iloc[0, 0]).replace('Class Group: ', '').strip()

print(f"Importing {len(df)} students from {class_group}...")

for idx, row in df.iterrows():
    name = str(row['name']).strip()
    
    # Generate username from name
    username = re.sub(r'[^a-zA-Z]', '', name.lower())[:15]
    password = "student123"
    
    # Hash password
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    try:
        cur.execute("""
            INSERT INTO users (username, password, full_name, role, department, level)
            VALUES (%s, %s, %s, 'student', %s, %s)
            ON CONFLICT (username) DO NOTHING
        """, (username, hashed, name, class_group[:3] if len(class_group) > 3 else 'GEN', class_group))
        
        print(f"✓ {name} -> {username}")
    except Exception as e:
        print(f"✗ {name}: {e}")

conn.commit()
cur.close()
conn.close()

print(f"\n✅ Import complete! Default password: student123")
