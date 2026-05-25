#!/usr/bin/env python3
"""
Complete RTB TVET Schools Migration
Based on Rwanda TVET structure with all major schools and their trades
"""
import sqlite3

conn = sqlite3.connect('quiz.db')
cursor = conn.cursor()

# Create tables
cursor.execute('''CREATE TABLE IF NOT EXISTS provinces (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS districts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    province_id INTEGER NOT NULL,
    FOREIGN KEY (province_id) REFERENCES provinces(id)
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS schools (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    district_id INTEGER NOT NULL,
    type TEXT,
    FOREIGN KEY (district_id) REFERENCES districts(id)
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    category TEXT
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS school_trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    school_id INTEGER NOT NULL,
    trade_id INTEGER NOT NULL,
    levels TEXT NOT NULL,
    FOREIGN KEY (school_id) REFERENCES schools(id),
    FOREIGN KEY (trade_id) REFERENCES trades(id),
    UNIQUE(school_id, trade_id)
)''')

# Add columns to users table
try:
    cursor.execute('ALTER TABLE users ADD COLUMN school_id INTEGER')
except: pass
try:
    cursor.execute('ALTER TABLE users ADD COLUMN trade_id INTEGER')
except: pass

print("📋 Creating provinces...")
provinces = [
    'Kigali City',
    'Eastern Province', 
    'Northern Province',
    'Southern Province',
    'Western Province'
]
for p in provinces:
    cursor.execute('INSERT OR IGNORE INTO provinces (name) VALUES (?)', (p,))

print("📋 Creating districts...")
districts = [
    ('Gasabo', 1), ('Kicukiro', 1), ('Nyarugenge', 1),
    ('Bugesera', 2), ('Gatsibo', 2), ('Kayonza', 2), ('Kirehe', 2), ('Ngoma', 2), ('Nyagatare', 2), ('Rwamagana', 2),
    ('Burera', 3), ('Gakenke', 3), ('Gicumbi', 3), ('Musanze', 3), ('Rulindo', 3),
    ('Gisagara', 4), ('Huye', 4), ('Kamonyi', 4), ('Muhanga', 4), ('Nyamagabe', 4), ('Nyanza', 4), ('Nyaruguru', 4), ('Ruhango', 4),
    ('Karongi', 5), ('Ngororero', 5), ('Nyabihu', 5), ('Nyamasheke', 5), ('Rubavu', 5), ('Rusizi', 5), ('Rutsiro', 5)
]
for name, prov_id in districts:
    cursor.execute('INSERT OR IGNORE INTO districts (name, province_id) VALUES (?, ?)', (name, prov_id))

print("📋 Creating all trades...")
trades = [
    ('Masonry', 'Construction'),
    ('Carpentry', 'Construction'),
    ('Joinery', 'Construction'),
    ('Plumbing', 'Construction'),
    ('Painting and Decoration', 'Construction'),
    ('Civil Construction', 'Construction'),
    ('Concrete Masonry', 'Construction'),
    ('Building Construction', 'Construction'),
    ('Domestic Electricity', 'Electrical'),
    ('Industrial Electricity', 'Electrical'),
    ('Electrical Installation', 'Electrical'),
    ('Electronic Services', 'Electrical'),
    ('Electronics Technology', 'Electrical'),
    ('Refrigeration and Air Conditioning', 'Electrical'),
    ('Auto Engine Mechanics', 'Automotive'),
    ('Automotive Engine Technology', 'Automotive'),
    ('Auto Electricity and Electronics Systems', 'Automotive'),
    ('Automotive Transmission Systems', 'Automotive'),
    ('Auto Body Repair', 'Automotive'),
    ('Motor Vehicle Mechanics', 'Automotive'),
    ('Computer Applications', 'ICT'),
    ('Computer System Technology', 'ICT'),
    ('Networking', 'ICT'),
    ('Software Development', 'ICT'),
    ('Hardware Maintenance', 'ICT'),
    ('Web Development', 'ICT'),
    ('Database Management', 'ICT'),
    ('Culinary Arts', 'Hospitality'),
    ('Food Production', 'Hospitality'),
    ('Hotel Management', 'Hospitality'),
    ('Restaurant Services', 'Hospitality'),
    ('Tourism', 'Hospitality'),
    ('Catering Services', 'Hospitality'),
    ('Accounting', 'Business'),
    ('Secretarial Studies', 'Business'),
    ('Business Administration', 'Business'),
    ('Office Management', 'Business'),
    ('Tailoring', 'Fashion'),
    ('Fashion Design', 'Fashion'),
    ('Garment Making', 'Fashion'),
    ('Welding', 'Metal Work'),
    ('Metal Fabrication', 'Metal Work'),
    ('Fitting and Welding', 'Metal Work'),
    ('Sheet Metal Work', 'Metal Work'),
    ('Interior Design', 'Design'),
    ('Graphic Design', 'Design'),
    ('Photography', 'Design'),
    ('Agriculture Technology', 'Agriculture'),
    ('Crop Production', 'Agriculture'),
    ('Animal Health', 'Agriculture'),
    ('Food Processing', 'Agriculture'),
    ('Bakery and Confectionery', 'Agriculture'),
    ('Hairdressing', 'Other'),
    ('Land Surveying', 'Other'),
    ('Solar Energy', 'Other'),
    ('Leather Work', 'Other')
]
for name, cat in trades:
    cursor.execute('INSERT OR IGNORE INTO trades (name, category) VALUES (?, ?)', (name, cat))

print("📋 Creating all RTB TVET schools...")
schools = [
    # IPRC Schools (6 major campuses)
    ('IPRC Kigali', 'Gasabo', 'Public'),
    ('IPRC Kicukiro', 'Kicukiro', 'Public'),
    ('IPRC Tumba', 'Karongi', 'Public'),
    ('IPRC Musanze', 'Musanze', 'Public'),
    ('IPRC Huye', 'Huye', 'Public'),
    ('IPRC Ngoma', 'Ngoma', 'Public'),
    
    # ETO Schools (Technical Official Schools)
    ('ETO Kigali', 'Nyarugenge', 'Public'),
    ('ETO Muhanga', 'Muhanga', 'Public'),
    ('ETO Nyanza', 'Nyanza', 'Public'),
    ('ETO Rwamagana', 'Rwamagana', 'Public'),
    ('ETO Rubavu', 'Rubavu', 'Public'),
    ('ETO Musanze', 'Musanze', 'Public'),
    ('ETO Byumba', 'Gicumbi', 'Public'),
    
    # District TVET Schools
    ('Nyamata TVET School', 'Bugesera', 'Public'),
    ('Nelson Mandela TVET School', 'Bugesera', 'Public'),
    ('Gahini TVET School', 'Kayonza', 'Public'),
    ('Nyagatare TVET School', 'Nyagatare', 'Public'),
    ('Gatsibo TVET School', 'Gatsibo', 'Public'),
    ('Kirehe TVET School', 'Kirehe', 'Public'),
    ('Burera TVET School', 'Burera', 'Public'),
    ('Gahunga TVET School', 'Burera', 'Public'),
    ('Kabona TVET School', 'Burera', 'Public'),
    ('Gicumbi TVET School', 'Gicumbi', 'Public'),
    ('Rushashi TVET School', 'Gakenke', 'Public'),
    ('Janja TVET School', 'Gakenke', 'Government-Aided'),
    ('Busengo TVET School', 'Gakenke', 'Private'),
    ('Rulindo TVET School', 'Rulindo', 'Public'),
    ('Gisagara TVET School', 'Gisagara', 'Public'),
    ('Kamonyi TVET School', 'Kamonyi', 'Public'),
    ('Nyamagabe TVET School', 'Nyamagabe', 'Public'),
    ('Nyaruguru TVET School', 'Nyaruguru', 'Public'),
    ('Ruhango TVET School', 'Ruhango', 'Public'),
    ('Ngororero TVET School', 'Ngororero', 'Public'),
    ('Nyabihu TVET School', 'Nyabihu', 'Public'),
    ('Nyamasheke TVET School', 'Nyamasheke', 'Public'),
    ('Rusizi TVET School', 'Rusizi', 'Public'),
    ('Rutsiro TVET School', 'Rutsiro', 'Public'),
    
    # Catholic/Church Schools
    ('Don Bosco Muhazi', 'Rwamagana', 'Private'),
    ('Don Bosco Gatenga', 'Kicukiro', 'Private'),
    ('GS Saint Joseph Kabgayi', 'Muhanga', 'Government-Aided'),
    ('GS Karubanda', 'Huye', 'Government-Aided'),
    ('GS Nyundo', 'Rubavu', 'Government-Aided'),
    ('GS Zaza', 'Ngoma', 'Government-Aided'),
    ('GS Rambura', 'Nyabihu', 'Government-Aided'),
    ('GS Mukarange', 'Kayonza', 'Government-Aided'),
    ('GS Shyogwe', 'Muhanga', 'Government-Aided'),
    ('ETAG Gitwe', 'Ruhango', 'Private'),
    ('Lycee Catholic St Martin Mataba', 'Gakenke', 'Private'),
    
    # Other Notable Schools
    ('Lycee de Kigali', 'Gasabo', 'Government-Aided'),
    ('Akilah Institute', 'Kicukiro', 'Private'),
    ('Rwanda Polytechnic', 'Kicukiro', 'Public'),
    ('Tumba College of Technology', 'Karongi', 'Public'),
]

for school_name, district_name, school_type in schools:
    cursor.execute('SELECT id FROM districts WHERE name = ?', (district_name,))
    result = cursor.fetchone()
    if result:
        district_id = result[0]
        cursor.execute('INSERT OR IGNORE INTO schools (name, district_id, type) VALUES (?, ?, ?)', 
                      (school_name, district_id, school_type))

print("📋 Mapping trades to schools...")

# Helper function to add school trades
def add_school_trades(school_name, trade_mappings):
    cursor.execute('SELECT id FROM schools WHERE name = ?', (school_name,))
    result = cursor.fetchone()
    if not result:
        return
    school_id = result[0]
    
    for trade_name, levels in trade_mappings:
        cursor.execute('SELECT id FROM trades WHERE name = ?', (trade_name,))
        trade_result = cursor.fetchone()
        if trade_result:
            trade_id = trade_result[0]
            cursor.execute('INSERT OR IGNORE INTO school_trades (school_id, trade_id, levels) VALUES (?, ?, ?)',
                          (school_id, trade_id, levels))

# IPRC Kigali - Comprehensive ICT, Engineering, Construction
add_school_trades('IPRC Kigali', [
    ('Software Development', '3,4,5'),
    ('Computer System Technology', '3,4,5'),
    ('Networking', '4,5'),
    ('Automotive Engine Technology', '3,4,5'),
    ('Electrical Installation', '3,4,5'),
    ('Electronics Technology', '4,5'),
    ('Civil Construction', '3,4,5'),
    ('Building Construction', '4,5'),
    ('Culinary Arts', '3,4'),
    ('Hotel Management', '4,5'),
    ('Accounting', '3,4,5'),
])

# IPRC Musanze - Engineering, Agriculture, ICT
add_school_trades('IPRC Musanze', [
    ('Automotive Engine Technology', '3,4,5'),
    ('Auto Electricity and Electronics Systems', '4,5'),
    ('Electrical Installation', '3,4,5'),
    ('Computer Applications', '3,4'),
    ('Networking', '4,5'),
    ('Agriculture Technology', '3,4,5'),
    ('Crop Production', '3,4'),
    ('Civil Construction', '3,4,5'),
    ('Welding', '3,4'),
])

# IPRC Huye - ICT, Business, Hospitality
add_school_trades('IPRC Huye', [
    ('Software Development', '3,4,5'),
    ('Computer System Technology', '3,4,5'),
    ('Networking', '4,5'),
    ('Accounting', '3,4,5'),
    ('Business Administration', '4,5'),
    ('Culinary Arts', '3,4,5'),
    ('Tourism', '3,4,5'),
    ('Hotel Management', '4,5'),
])

# IPRC Tumba - Construction, Electrical, ICT
add_school_trades('IPRC Tumba', [
    ('Civil Construction', '3,4,5'),
    ('Building Construction', '4,5'),
    ('Electrical Installation', '3,4,5'),
    ('Industrial Electricity', '4,5'),
    ('Computer Applications', '3,4'),
    ('Software Development', '4,5'),
    ('Masonry', '1,3,4'),
    ('Carpentry', '1,3,4'),
])

# IPRC Kicukiro - ICT, Electronics, Business
add_school_trades('IPRC Kicukiro', [
    ('Software Development', '3,4,5'),
    ('Computer System Technology', '3,4,5'),
    ('Networking', '4,5'),
    ('Electronics Technology', '3,4,5'),
    ('Accounting', '3,4,5'),
    ('Secretarial Studies', '3,4'),
])

# IPRC Ngoma - Agriculture, Construction, Automotive
add_school_trades('IPRC Ngoma', [
    ('Agriculture Technology', '3,4,5'),
    ('Crop Production', '3,4,5'),
    ('Animal Health', '3,4,5'),
    ('Automotive Engine Technology', '3,4'),
    ('Civil Construction', '3,4,5'),
    ('Masonry', '1,3,4'),
])

# ETO Schools - Technical trades focus
eto_trades = [
    ('Masonry', '1,3,4'),
    ('Carpentry', '1,3,4'),
    ('Domestic Electricity', '3,4'),
    ('Industrial Electricity', '4,5'),
    ('Welding', '1,3,4'),
    ('Plumbing', '3,4'),
    ('Auto Engine Mechanics', '3,4'),
]

for school in ['ETO Kigali', 'ETO Muhanga', 'ETO Nyanza', 'ETO Rwamagana', 'ETO Rubavu', 'ETO Musanze', 'ETO Byumba']:
    add_school_trades(school, eto_trades)

# District TVET Schools - Basic trades
district_trades = [
    ('Masonry', '1,3'),
    ('Carpentry', '1,3'),
    ('Domestic Electricity', '3'),
    ('Tailoring', '1,3'),
    ('Welding', '1,3'),
    ('Computer Applications', '3'),
]

for school in ['Nyamata TVET School', 'Gahini TVET School', 'Nyagatare TVET School', 'Gatsibo TVET School', 
               'Kirehe TVET School', 'Burera TVET School', 'Gicumbi TVET School', 'Rulindo TVET School',
               'Gisagara TVET School', 'Kamonyi TVET School', 'Nyamagabe TVET School', 'Nyaruguru TVET School',
               'Ruhango TVET School', 'Ngororero TVET School', 'Nyabihu TVET School', 'Nyamasheke TVET School',
               'Rusizi TVET School', 'Rutsiro TVET School']:
    add_school_trades(school, district_trades)

# Don Bosco Schools - Technical excellence
don_bosco_trades = [
    ('Automotive Engine Technology', '3,4,5'),
    ('Auto Electricity and Electronics Systems', '4,5'),
    ('Electrical Installation', '3,4,5'),
    ('Electronics Technology', '4,5'),
    ('Computer System Technology', '3,4'),
    ('Welding', '3,4'),
    ('Metal Fabrication', '3,4'),
]

add_school_trades('Don Bosco Muhazi', don_bosco_trades)
add_school_trades('Don Bosco Gatenga', don_bosco_trades)

# Catholic Schools - Diverse trades
gs_trades = [
    ('Masonry', '1,3,4'),
    ('Carpentry', '1,3,4'),
    ('Domestic Electricity', '3,4'),
    ('Industrial Electricity', '4,5'),
    ('Tailoring', '1,3,4'),
    ('Accounting', '3,4'),
    ('Computer Applications', '3,4'),
]

for school in ['GS Saint Joseph Kabgayi', 'GS Karubanda', 'GS Nyundo', 'GS Zaza', 'GS Rambura', 'GS Mukarange', 'GS Shyogwe']:
    add_school_trades(school, gs_trades)

# Specialized schools
add_school_trades('Akilah Institute', [
    ('Software Development', '4,5'),
    ('Computer System Technology', '4,5'),
    ('Business Administration', '4,5'),
    ('Accounting', '4,5'),
])

add_school_trades('Rwanda Polytechnic', [
    ('Software Development', '3,4,5,6'),
    ('Computer System Technology', '3,4,5,6'),
    ('Networking', '4,5,6'),
    ('Civil Construction', '3,4,5,6'),
    ('Electrical Installation', '3,4,5,6'),
    ('Electronics Technology', '4,5,6'),
])

add_school_trades('Nelson Mandela TVET School', [
    ('Masonry', '3,4,5'),
    ('Domestic Electricity', '3'),
    ('Industrial Electricity', '4,5'),
    ('Tailoring', '3'),
    ('Welding', '3,4'),
])

conn.commit()

# Print summary
cursor.execute("SELECT COUNT(*) FROM provinces")
print(f"\n✅ Provinces: {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM districts")
print(f"✅ Districts: {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM schools")
print(f"✅ Schools: {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM trades")
print(f"✅ Trades: {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM school_trades")
print(f"✅ School-Trade mappings: {cursor.fetchone()[0]}")

print("\n📊 Sample school-trade mappings:")
cursor.execute('''
    SELECT s.name, t.name, st.levels 
    FROM school_trades st
    JOIN schools s ON st.school_id = s.id
    JOIN trades t ON st.trade_id = t.id
    LIMIT 10
''')
for row in cursor.fetchall():
    print(f"  • {row[0]}: {row[1]} (Levels: {row[2]})")

conn.close()
print("\n✅ Complete RTB TVET migration successful!")
