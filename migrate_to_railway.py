"""
Create tables and import data from SQLite to Railway PostgreSQL
"""
import sqlite3
import json
import psycopg2
from urllib.parse import urlparse

# Railway PostgreSQL connection
DATABASE_URL = "postgresql://postgres:etFcYsqQeDTEJBvBGdZOVNlVdLLPDvLG@shinkansen.proxy.rlwy.net:42954/railway"

def create_tables_from_sqlite():
    """Create PostgreSQL tables by reading SQLite schema"""
    print("=== CREATING TABLES ===\n")
    
    # Connect to SQLite to get schema
    sqlite_conn = sqlite3.connect('quiz.db')
    sqlite_cursor = sqlite_conn.cursor()
    
    # Connect to PostgreSQL
    pg_result = urlparse(DATABASE_URL)
    pg_conn = psycopg2.connect(
        host=pg_result.hostname,
        port=pg_result.port,
        database=pg_result.path[1:],
        user=pg_result.username,
        password=pg_result.password
    )
    pg_cursor = pg_conn.cursor()
    
    # Get all tables from SQLite
    sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = [row[0] for row in sqlite_cursor.fetchall()]
    
    print(f"Found {len(tables)} tables to create\n")
    
    # Create each table
    for table in tables:
        try:
            # Get table schema from SQLite
            sqlite_cursor.execute(f"PRAGMA table_info({table})")
            columns = sqlite_cursor.fetchall()
            
            # Build CREATE TABLE statement for PostgreSQL
            col_defs = []
            for col in columns:
                col_name = col[1]
                col_type = col[2]
                
                # Convert SQLite types to PostgreSQL
                if 'INTEGER' in col_type.upper():
                    pg_type = 'INTEGER'
                elif 'TEXT' in col_type.upper():
                    pg_type = 'TEXT'
                elif 'VARCHAR' in col_type.upper():
                    pg_type = col_type
                elif 'BOOLEAN' in col_type.upper():
                    pg_type = 'BOOLEAN'
                elif 'DATETIME' in col_type.upper():
                    pg_type = 'TIMESTAMP'
                elif 'FLOAT' in col_type.upper() or 'REAL' in col_type.upper():
                    pg_type = 'FLOAT'
                elif 'JSON' in col_type.upper():
                    pg_type = 'JSONB'
                else:
                    pg_type = col_type
                
                # Primary key
                if col[5] == 1:  # pk flag
                    col_defs.append(f"{col_name} {pg_type} PRIMARY KEY")
                else:
                    col_defs.append(f"{col_name} {pg_type}")
            
            # Create table
            create_sql = f"CREATE TABLE IF NOT EXISTS {table} ({', '.join(col_defs)})"
            pg_cursor.execute(create_sql)
            pg_conn.commit()
            
            print(f"✅ Created table: {table}")
            
        except Exception as e:
            print(f"❌ Error creating {table}: {e}")
    
    pg_conn.close()
    sqlite_conn.close()
    print("\n✅ Table creation complete!\n")

def import_data():
    """Import data from SQLite to PostgreSQL"""
    print("=== IMPORTING DATA ===\n")
    
    # Load exported data
    with open('postgres_migration_data.json', 'r') as f:
        data = json.load(f)
    
    # Connect to PostgreSQL
    pg_result = urlparse(DATABASE_URL)
    pg_conn = psycopg2.connect(
        host=pg_result.hostname,
        port=pg_result.port,
        database=pg_result.path[1:],
        user=pg_result.username,
        password=pg_result.password
    )
    pg_cursor = pg_conn.cursor()
    
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
    
    total_imported = 0
    
    for table in tables:
        if table not in data or not data[table]['rows']:
            print(f"⏭️  Skipping {table} (no data)")
            continue
        
        table_data = data[table]
        columns = table_data['columns']
        rows = table_data['rows']
        
        imported = 0
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
                    elif isinstance(val, str):
                        # Handle JSON arrays
                        if val.startswith('[') or val.startswith('{'):
                            try:
                                values.append(json.loads(val))
                            except:
                                values.append(val)
                        else:
                            values.append(val)
                    else:
                        values.append(str(val))
                
                sql = f"INSERT INTO {table} ({col_names}) VALUES ({placeholders}) ON CONFLICT DO NOTHING"
                pg_cursor.execute(sql, values)
                imported += 1
                total_imported += 1
                
            except Exception as e:
                print(f"  ⚠️  Error in {table}: {str(e)[:80]}")
        
        pg_conn.commit()
        print(f"✅ Imported {table}: {imported}/{len(rows)} rows")
    
    pg_conn.close()
    print(f"\n✅ Total imported: {total_imported} records")

def verify_data():
    """Verify data was imported correctly"""
    print("\n=== VERIFYING DATA ===\n")
    
    pg_result = urlparse(DATABASE_URL)
    pg_conn = psycopg2.connect(
        host=pg_result.hostname,
        port=pg_result.port,
        database=pg_result.path[1:],
        user=pg_result.username,
        password=pg_result.password
    )
    pg_cursor = pg_conn.cursor()
    
    tables = ['provinces', 'districts', 'schools', 'trades', 'school_trades', 'users']
    
    for table in tables:
        pg_cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = pg_cursor.fetchone()[0]
        print(f"  {table}: {count} rows")
    
    pg_conn.close()

if __name__ == "__main__":
    print("="*60)
    print("MIGRATING SQLITE TO RAILWAY POSTGRESQL")
    print("="*60)
    print()
    
    # Step 1: Create tables
    create_tables_from_sqlite()
    
    # Step 2: Import data
    import_data()
    
    # Step 3: Verify
    verify_data()
    
    print("\n" + "="*60)
    print("✅ MIGRATION COMPLETE!")
    print("="*60)
