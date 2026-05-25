import os
import psycopg2

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:etFcYsqQeDTEJBvBGdZOVNlVdLLPDvLG@shinkansen.proxy.rlwy.net:42954/railway')

print("Connecting to database...")

try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    print("Connected successfully!")
    
    with open('assignment_migration.sql', 'r', encoding='utf-8') as f:
        sql = f.read()
    
    print("Running migration...")
    cursor.execute(sql)
    conn.commit()
    
    print("Migration completed successfully!")
    
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name LIKE 'assignment%' OR table_name = 'submission_files'
        ORDER BY table_name
    """)
    
    tables = cursor.fetchall()
    print(f"\nCreated {len(tables)} tables:")
    for table in tables:
        print(f"  - {table[0]}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
    print("\nPlease check:")
    print("1. Railway DATABASE_URL is correct")
    print("2. Network connection is stable")
    print("3. Database credentials are valid")
