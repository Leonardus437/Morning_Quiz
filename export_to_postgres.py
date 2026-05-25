"""
Export SQLite data to PostgreSQL-compatible format
Run this locally, then import to Railway PostgreSQL
"""
import sqlite3
import json
import os

def export_sqlite_to_json():
    """Export all data from SQLite to JSON files for PostgreSQL import"""
    conn = sqlite3.connect('quiz.db')
    cursor = conn.cursor()
    
    # Tables to export (in dependency order)
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
    
    exported_data = {}
    
    for table in tables:
        try:
            # Get column names
            cursor.execute(f"PRAGMA table_info({table})")
            columns = [col[1] for col in cursor.fetchall()]
            
            # Get all rows
            cursor.execute(f"SELECT * FROM {table}")
            rows = cursor.fetchall()
            
            # Convert to list of dicts
            data = []
            for row in rows:
                row_dict = {}
                for i, col in enumerate(columns):
                    row_dict[col] = row[i]
                data.append(row_dict)
            
            exported_data[table] = {
                'columns': columns,
                'rows': data
            }
            print(f"Exported {table}: {len(data)} rows")
            
        except Exception as e:
            print(f"Error exporting {table}: {e}")
    
    conn.close()
    
    # Save to JSON file
    with open('postgres_migration_data.json', 'w') as f:
        json.dump(exported_data, f, indent=2, default=str)
    
    print(f"\nExported to postgres_migration_data.json")
    print(f"Total tables: {len(exported_data)}")
    return exported_data

def generate_postgres_inserts():
    """Generate PostgreSQL INSERT statements"""
    with open('postgres_migration_data.json', 'r') as f:
        data = json.load(f)
    
    sql_statements = []
    
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
    
    for table in tables:
        if table not in data:
            continue
            
        table_data = data[table]
        columns = table_data['columns']
        rows = table_data['rows']
        
        if not rows:
            continue
        
        for row in rows:
            # Build INSERT statement
            col_names = ', '.join(columns)
            placeholders = ', '.join(['%s'] * len(columns))
            values = []
            
            for col in columns:
                val = row.get(col)
                # Convert Python None to SQL NULL
                if val is None:
                    values.append(None)
                elif isinstance(val, bool):
                    values.append(val)
                elif isinstance(val, (int, float)):
                    values.append(val)
                else:
                    values.append(str(val))
            
            sql = f"INSERT INTO {table} ({col_names}) VALUES ({placeholders});"
            sql_statements.append({'sql': sql, 'values': values})
    
    # Save to file
    with open('postgres_inserts.sql', 'w') as f:
        for item in sql_statements:
            # Escape single quotes for SQL
            sql = item['sql']
            values = item['values']
            # Simple format for manual execution
            f.write(f"-- {sql[:50]}...\n")
    
    print(f"Generated {len(sql_statements)} INSERT statements")
    print("Saved to postgres_inserts.sql (reference)")
    print("\nUse postgres_migration_data.json with Python script to import")

if __name__ == "__main__":
    print("=== EXPORTING SQLITE TO POSTGRESQL FORMAT ===\n")
    export_sqlite_to_json()
    print("\n=== GENERATING INSERT STATEMENTS ===\n")
    generate_postgres_inserts()
    
    print("\n" + "="*50)
    print("NEXT STEPS:")
    print("="*50)
    print("1. Add PostgreSQL to Railway project")
    print("2. Set DATABASE_URL environment variable in Railway")
    print("3. Run: python import_to_postgres.py (will create this next)")
    print("="*50)
