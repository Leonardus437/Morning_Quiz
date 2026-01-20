import sqlite3

# Connect to database
conn = sqlite3.connect('backend/quiz.db')
cursor = conn.cursor()

# Update lesson levels from short to full format
updates = [
    ('L3', 'Level 3'),
    ('L4', 'Level 4'),
    ('L5', 'Level 5'),
    ('L6', 'Level 6')
]

for old, new in updates:
    cursor.execute("UPDATE lessons SET level = ? WHERE level = ?", (new, old))
    print(f"Updated lessons: {old} -> {new} ({cursor.rowcount} rows)")

conn.commit()
conn.close()
print("\nDone! Lessons updated.")
