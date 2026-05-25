"""
Import SQLite data to PostgreSQL (run AFTER Railway PostgreSQL is set up)
Set DATABASE_URL environment variable first!
"""
import sqlite3
import json
import os
import psycopg2
from urllib.parse import urlparse

def get_postgres_connection():
    """Get PostgreSQL connection from DATABASE_URL"""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        raise ValueError("DATABASE_URL environment variable not set!")
    
    # Parse Railway PostgreSQL URL
    result = urlparse(database_url)
    
    return psycopg2.connect(
        host=result.hostname,
        port=result.port or 5432,
        database=result.path[1:],  # Remove leading /
        user=result.username,
        password=result.password
    )

def import_to_postgres():
    """Import data from JSON to PostgreSQL"""
    print("=== IMPORTING TO POSTGRESQL ===\n")
    
    # Load exported data
    with open('postgres_migration_data.json', 'r') as f:
        data = json.load(f)
    
    # Connect to PostgreSQL
    try:
        pg_conn = get_postgres_connection()
        pg_cursor = pg_conn.cursor()
        print("✅ Connected to PostgreSQL")
    except Exception as e:
        print(f"❌ Failed to connect to PostgreSQL: {e}")
        return
    
    # Tables in dependency order
    tables = [
        'provinces',
        'districts',
        'schools',
        'school_types',
        'trades',
        'school_trades',
        'users',
        'lessons',
        'teacher_lessons',
        'questions',
        'quizzes',
        'quiz_questions',
        'quiz_attempts',
        'student_answers',
        'notifications'
    ]
    
    imported = 0
    errors = 0
    
    for table in tables:
        if table not in data:
            continue
            
        table_data = data[table]
        columns = table_data['columns']
        rows = table_data['rows']
        
        if not rows:
            print(f"⏭️  Skipping {table} (no data)")
            continue
        
        for row in rows:
            try:
                # Build INSERT statement
                col_names = ', '.join(columns)
                placeholders = ', '.join(['%s'] * len(columns))
                values = []
                
                for col in columns:
                    val = row.get(col)
                    if val is None:
                        values.append(None)
                    elif isinstance(val, bool):
                        values.append(val)
                    elif isinstance(val, (int, float)):
                        values.append(val)
                    elif isinstance(val, str) and val.startswith('['):
                        # JSON array
                        values.append(json.loads(val))
                    else:
                        values.append(str(val))
                
                # Use UPSERT (ON CONFLICT) to avoid duplicates
                sql = f"""
                    INSERT INTO {table} ({col_names}) 
                    VALUES ({placeholders})
                    ON CONFLICT DO NOTHING
                """
                
                pg_cursor.execute(sql, values)
                imported += 1
                
            except Exception as e:
                errors += 1
                if errors <= 5:  # Only show first 5 errors
                    print(f"❌ Error inserting into {table}: {e}")
        
        pg_conn.commit()
        print(f"✅ Imported {table}: {len(rows)} rows")
    
    pg_conn.close()
    
    print(f"\n" + "="*50)
    print(f"IMPORT COMPLETE")
    print(f"  Imported: {imported} rows")
    print(f"  Errors: {errors}")
    print("="*50)

if __name__ == "__main__":
    import_to_postgres()
