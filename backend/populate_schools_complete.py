#!/usr/bin/env python3
"""
Populate database with complete school hierarchy from the reaccredited schools document
Province -> District -> School -> Trade -> Level
"""

import sqlite3
import json
import re

# District to Province mapping
DISTRICT_PROVINCE = {
    'BUGESERA': 'Eastern Province',
    'GATSIBO': 'Eastern Province',
    'KAYONZA': 'Eastern Province',
    'BURERA': 'Northern Province',
    'GAKENKE': 'Northern Province',
    'GICUMBI': 'Northern Province',
    'KICUKIRO': 'Kigali City',
    'GASABO': 'Kigali City',
    'HUYE': 'Southern Province',
    'GISAGARA': 'Southern Province',
    'KAMONYI': 'Southern Province',
    'KARONGI': 'Western Province'
}

def parse_levels(trade_text):
    """Extract levels from trade text (e.g., 'L3-5', 'L1', 'L3-L5', 'L4-5')"""
    levels = []
    
    # Match patterns like L3-5, L3-L5, L1, etc.
    if 'L1' in trade_text:
        levels.append('L1')
    if re.search(r'L[23456]', trade_text):
        # Extract L3-5 or L3-L5 patterns
        if re.search(r'L3[\-]?[L]?[45]', trade_text):
            levels.extend(['L3', 'L4', 'L5'])
        elif 'L4' in trade_text and 'L5' in trade_text:
            levels.extend(['L4', 'L5'])
        elif 'L2' in trade_text:
            levels.append('L2')
    
    return list(set(levels)) if levels else ['L3', 'L4', 'L5']

def init_database(db_path):
    """Initialize database with schema"""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # Create tables
    # Drop existing tables to recreate with correct schema
    cur.execute('DROP TABLE IF EXISTS school_trades')
    cur.execute('DROP TABLE IF EXISTS schools')
    cur.execute('DROP TABLE IF EXISTS districts')
    cur.execute('DROP TABLE IF EXISTS provinces')
    cur.execute('DROP TABLE IF EXISTS trades')
    
    cur.executescript('''
        -- Provinces
        CREATE TABLE provinces (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            code TEXT UNIQUE
        );
        
        -- Districts
        CREATE TABLE districts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            province_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            code TEXT,
            FOREIGN KEY (province_id) REFERENCES provinces(id),
            UNIQUE(province_id, name)
        );
        
        -- Schools
        CREATE TABLE schools (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            district_id INTEGER NOT NULL,
            province_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            code TEXT,
            school_type TEXT,
            status TEXT,
            boarding_status TEXT,
            sector TEXT,
            is_active INTEGER DEFAULT 1,
            FOREIGN KEY (district_id) REFERENCES districts(id),
            FOREIGN KEY (province_id) REFERENCES provinces(id),
            UNIQUE(district_id, name)
        );
        
        -- Trades
        CREATE TABLE trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            code TEXT,
            category TEXT
        );
        
        -- School Trades (junction table with levels)
        CREATE TABLE school_trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            school_id INTEGER NOT NULL,
            trade_id INTEGER NOT NULL,
            levels_offered TEXT,
            is_active INTEGER DEFAULT 1,
            FOREIGN KEY (school_id) REFERENCES schools(id),
            FOREIGN KEY (trade_id) REFERENCES trades(id),
            UNIQUE(school_id, trade_id)
        );
        
        CREATE INDEX idx_districts_province ON districts(province_id);
        CREATE INDEX idx_schools_district ON schools(district_id);
        CREATE INDEX idx_schools_province ON schools(province_id);
        CREATE INDEX idx_school_trades_school ON school_trades(school_id);
    ''')
    
    conn.commit()
    return conn

def populate_schools(conn):
    """Populate with actual schools from the document"""
    cur = conn.cursor()
    
    # Insert provinces
    provinces = {
        'Eastern Province': 'EP',
        'Northern Province': 'NP',
        'Southern Province': 'SP',
        'Western Province': 'WP',
        'Kigali City': 'KC'
    }
    
    for prov_name, prov_code in provinces.items():
        cur.execute('INSERT OR IGNORE INTO provinces (name, code) VALUES (?, ?)', (prov_name, prov_code))
    
    conn.commit()
    
    # School data extracted from the document
    schools_data = [
        # BUGESERA DISTRICT
        {'district': 'BUGESERA', 'name': 'GASORE SERGE FOUNDATION VTC', 'type': 'VTC', 'status': 'Private', 'boarding': 'Day', 'trades': [('Tailoring', 'L1')]},
        {'district': 'BUGESERA', 'name': 'NELSON MANDELA TSS', 'type': 'TSS', 'status': 'Public', 'boarding': 'Boarding', 'trades': [('Building construction', 'L3-5'), ('Manufacturing technology', 'L3-5'), ('Electrical Technology', 'L3-5'), ('Fashion Design', 'L3-5')]},
        {'district': 'BUGESERA', 'name': 'LYCEE DE LA SAINTE TRINITE-APED TSS', 'type': 'TSS', 'status': 'Private', 'boarding': 'Mixed', 'trades': [('Building construction', 'L3-5'), ('Electrical technology', 'L3-5')]},
        {'district': 'BUGESERA', 'name': 'RUHUHA VTC', 'type': 'VTC', 'status': 'Public', 'boarding': 'Mixed', 'trades': [('Tailoring', 'L1'), ('Hairdressing', 'L1')]},
        {'district': 'BUGESERA', 'name': 'GS RUTONDE TSS', 'type': 'TSS', 'status': 'Public', 'boarding': 'Day', 'trades': [('Building Construction', 'L3-5'), ('Electrical Technology', 'L3-5')]},
        {'district': 'BUGESERA', 'name': 'NDAMA TSS', 'type': 'TSS', 'status': 'Government-aided', 'boarding': 'Day', 'trades': [('Animal health', 'L3-5'), ('Fashion design', 'L3-5')]},
        {'district': 'BUGESERA', 'name': 'EPR NYAMIRAMA VTC', 'type': 'VTC', 'status': 'Private', 'boarding': 'Day', 'trades': [('Tailoring', 'L1'), ('Masonry', 'L1'), ('Welding', 'L1')]},
        {'district': 'BUGESERA', 'name': 'GS GIHINGA TSS', 'type': 'TSS', 'status': 'Public', 'boarding': 'Day', 'trades': [('Building Construction', 'L3-5'), ('Plumbing Technology', 'L3-5')]},
        {'district': 'BUGESERA', 'name': 'GS KAMABARE TSS', 'type': 'TSS', 'status': 'Public', 'boarding': 'Day', 'trades': [('Building Construction', 'L3-5'), ('Electrical Technology', 'L3-5')]},
        {'district': 'BUGESERA', 'name': 'NYAMATA TSS', 'type': 'TSS', 'status': 'Public', 'boarding': 'Boarding', 'trades': [('Building construction', 'L3-5'), ('Networking and Internet technologies', 'L3-5'), ('Fashion design', 'L3-5'), ('Wood technology', 'L3-5'), ('Electrical technology', 'L3-5'), ('Renewable energy', 'L3-5'), ('Manufacturing technology', 'L3-5'), ('Land surveying', 'L3-5'), ('Electronics and telecommunication', 'L3-5'), ('Interior design', 'L3-5')]},
        
        # BURERA DISTRICT
        {'district': 'BURERA', 'name': 'ES GAHUNGA TSS', 'type': 'TSS', 'status': 'Private', 'boarding': 'Boarding', 'trades': [('Automobile technology', 'L3-5'), ('Electronics and telecommunication', 'L3-5'), ('Building construction', 'L3-5'), ('Agriculture', 'L3-5'), ('Electrical Technology', 'L3-5')]},
        {'district': 'BURERA', 'name': 'CEPEM TSS', 'type': 'TSS', 'status': 'Private', 'boarding': 'Boarding', 'trades': [('Building construction', 'L3-5'), ('Food and Beverage operations', 'L3-5'), ('Tourism', 'L3-5')]},
        {'district': 'BURERA', 'name': 'GS Bungwe TSS', 'type': 'TSS', 'status': 'Gov Aided', 'boarding': 'Day', 'trades': [('Building construction', 'L3-5'), ('Agriculture', 'L3-5')]},
        {'district': 'BURERA', 'name': 'MURWA TSS', 'type': 'TSS', 'status': 'Gov Aided', 'boarding': 'Boarding', 'trades': [('Building Construction', 'L3-5'), ('Wood technology', 'L3-5')]},
        {'district': 'BURERA', 'name': 'Kabona TSS', 'type': 'TSS', 'status': 'Public', 'boarding': 'Boarding', 'trades': [('Building construction', 'L3-5'), ('Wood technology', 'L3-5'), ('Automobile Technology', 'L3-5')]},
        
        # GAKENKE DISTRICT
        {'district': 'GAKENKE', 'name': 'ES NYACYINA', 'type': 'TSS', 'status': 'Gov aided', 'boarding': 'DAY', 'trades': [('Building Construction', 'L3-5'), ('Agriculture', 'L3-5')]},
        {'district': 'GAKENKE', 'name': 'GS KIREBE TSS', 'type': 'TSS', 'status': 'PUBLIC', 'boarding': 'DAY', 'trades': [('Electrical Technology', 'L3-5'), ('Building Construction', 'L3-5')]},
        {'district': 'GAKENKE', 'name': 'ES GATONDE TSS', 'type': 'TSS', 'status': 'PUBLIC', 'boarding': 'DAY', 'trades': [('Building Construction', 'L3-5'), ('Manufacturing technology', 'L3-5')]},
        {'district': 'GAKENKE', 'name': 'JANJA TSS', 'type': 'TSS', 'status': 'Gov aided', 'boarding': 'Boarding', 'trades': [('Building Construction', 'L3-5'), ('Wood Technology', 'L3-5'), ('Fashion Design', 'L3-5'), ('Electrical Technology', 'L3-5'), ('Masonry', 'L1'), ('Tailoring', 'L1'), ('Carpentry', 'L1'), ('Domestic Electricity', 'L1')]},
        
        # GASABO DISTRICT
        {'district': 'GASABO', 'name': 'SOS TSS', 'type': 'TSS', 'status': 'PRIVATE', 'boarding': 'Boarding and Day', 'trades': [('Software Development', 'L3-5'), ('Networking and Internet Technology', 'L3-5'), ('Electronics and Telecommunication', 'L3-5'), ('Computer System and Architecture', 'L3-5')]},
        {'district': 'GASABO', 'name': 'WORLD MISSION TSS', 'type': 'TSS', 'status': 'PRIVATE', 'boarding': 'Day', 'trades': [('Multimedia Production', 'L3-5'), ('Software Development', 'L3-5'), ('Networking and Internet Technology', 'L3-5')]},
        {'district': 'GASABO', 'name': 'GS RUGANDO TSS', 'type': 'TSS', 'status': 'PUBLIC', 'boarding': 'Day', 'trades': [('Software Development', 'L3-5'), ('Networking and Internet Technology', 'L3-5')]},
        
        # GICUMBI DISTRICT
        {'district': 'GICUMBI', 'name': 'GICUMBI TSS', 'type': 'TSS', 'status': 'Public', 'boarding': 'Boarding', 'trades': [('Electrical Technology', 'L3-5')]},
        {'district': 'GICUMBI', 'name': 'MULINDI TSS', 'type': 'TSS', 'status': 'Public', 'boarding': 'Boarding', 'trades': [('Computer Systems and Architecture', 'L3-5'), ('Networking and Internet Technology', 'L3-5'), ('Electronics and Telecommunication', 'L3-5')]},
        
        # GISAGARA DISTRICT
        {'district': 'GISAGARA', 'name': 'GIKONKO TSS', 'type': 'TSS', 'status': 'PUBLIC', 'boarding': 'Mixed', 'trades': [('Tailoring', 'L1'), ('Hairdressing', 'L1'), ('Masonry', 'L1'), ('Carpentry', 'L1'), ('Building Construction', 'L3-5'), ('Electrical Technology', 'L3-5'), ('Software Development', 'L3-5')]},
        {'district': 'GISAGARA', 'name': 'MUSHA ADVENTIST TSS', 'type': 'TSS', 'status': 'Government-aided', 'boarding': 'Boarding', 'trades': [('Building Construction', 'L3-5'), ('Electrical Technology', 'L3-5')]},
        
        # HUYE DISTRICT
        {'district': 'HUYE', 'name': 'IPRC SOUTH TSS', 'type': 'TSS', 'status': 'PUBLIC', 'boarding': 'Boarding', 'trades': [('Building Construction', 'L3-5'), ('Electrical Technology', 'L3-5'), ('Automobile Technology', 'L3-5'), ('Manufacturing Technology', 'L3-5'), ('Electronics and Telecommunication', 'L3-5')]},
        {'district': 'HUYE', 'name': 'MARABA TSS', 'type': 'TSS', 'status': 'PUBLIC', 'boarding': 'Day', 'trades': [('Tailoring', 'L1'), ('Masonry', 'L1'), ('Welding', 'L1'), ('Carpentry', 'L1'), ('Building Construction', 'L3-5'), ('Fashion Design', 'L3-5')]},
        
        # KAMONYI DISTRICT
        {'district': 'KAMONYI', 'name': 'College APPEC REMERA RUKOMA', 'type': 'TSS', 'status': 'Government Aided', 'boarding': 'Boarding', 'trades': [('Software Development', 'L3-5'), ('Computer System and Architecture', 'L3-5'), ('Building Construction', 'L3-5')]},
        {'district': 'KAMONYI', 'name': 'KIGESE TSS', 'type': 'TSS', 'status': 'PUBLIC', 'boarding': 'Day', 'trades': [('Tailoring', 'L1'), ('Masonry', 'L1'), ('Carpentry', 'L1'), ('Building Construction', 'L3-5'), ('Fashion Design', 'L3-5')]},
        
        # KARONGI DISTRICT
        {'district': 'KARONGI', 'name': 'IPRC KARONGI TSS', 'type': 'TSS', 'status': 'Public', 'boarding': 'Boarding', 'trades': [('Building Construction', 'L3-5'), ('Electrical Technology', 'L3-5'), ('Automobile Technology', 'L3-5'), ('Manufacturing Technology', 'L3-5')]},
        
        # GATSIBO DISTRICT
        {'district': 'GATSIBO', 'name': 'College Baptiste de Ngarama (COBANGA)', 'type': 'TSS', 'status': 'PRIVATE', 'boarding': 'Boarding', 'trades': [('Tourism', 'L3-5'), ('Software Development', 'L3-5')]},
        {'district': 'GATSIBO', 'name': 'BENEBIKIRA TSS', 'type': 'TSS', 'status': 'PRIVATE', 'boarding': 'Boarding', 'trades': [('Building Construction', 'L3-5'), ('Food & Beverage Operations', 'L3-5'), ('Wood Technology', 'L3-5'), ('Fashion Design', 'L3-5')]},
        
        # KAYONZA DISTRICT
        {'district': 'KAYONZA', 'name': 'KAYONZA TSS', 'type': 'TSS', 'status': 'PRIVATE', 'boarding': 'Mixed', 'trades': [('Culinary arts', 'L1'), ('Food and Beverage Operations', 'L3-5')]},
        {'district': 'KAYONZA', 'name': 'GS RUKARA TSS', 'type': 'TSS', 'status': 'Gov Aided', 'boarding': 'Day', 'trades': [('Electrical Technology', 'L3-5'), ('Building Construction', 'L3-5')]},
        
        # KICUKIRO DISTRICT
        {'district': 'KICUKIRO', 'name': 'GS AYABARAYA TSS', 'type': 'TSS', 'status': 'PUBLIC', 'boarding': 'DAY', 'trades': [('Automobile Technology', 'L3-5'), ('Manufacturing Technology', 'L3-5')]},
        {'district': 'KICUKIRO', 'name': 'IPRC KIGALI TSS', 'type': 'TSS', 'status': 'PUBLIC', 'boarding': 'Day', 'trades': [('Building construction', 'L3-5'), ('Public works', 'L3-5'), ('Networking and Internet technology', 'L3-5'), ('Electrical technology', 'L3-5'), ('Automobile technology', 'L3-5'), ('Manufacturing technology', 'L3-5'), ('Electronic and telecommunication', 'L3-5')]},
    ]
    
    # Insert districts and schools
    for school_data in schools_data:
        district_name = school_data['district']
        province_name = DISTRICT_PROVINCE.get(district_name, 'Eastern Province')
        
        # Get province ID
        cur.execute('SELECT id FROM provinces WHERE name = ?', (province_name,))
        province_id = cur.fetchone()[0]
        
        # Insert district
        cur.execute('INSERT OR IGNORE INTO districts (province_id, name, code) VALUES (?, ?, ?)',
                   (province_id, district_name, district_name[:3].upper()))
        cur.execute('SELECT id FROM districts WHERE name = ? AND province_id = ?', (district_name, province_id))
        district_id = cur.fetchone()[0]
        
        # Insert school
        cur.execute('''INSERT OR IGNORE INTO schools 
                      (district_id, province_id, name, school_type, status, boarding_status, is_active)
                      VALUES (?, ?, ?, ?, ?, ?, 1)''',
                   (district_id, province_id, school_data['name'], school_data['type'],
                    school_data['status'], school_data['boarding']))
        
        cur.execute('SELECT id FROM schools WHERE name = ? AND district_id = ?',
                   (school_data['name'], district_id))
        school_id = cur.fetchone()[0]
        
        # Insert trades
        for trade_name, level_text in school_data['trades']:
            # Insert trade if not exists
            cur.execute('INSERT OR IGNORE INTO trades (name, category) VALUES (?, ?)',
                       (trade_name, 'Technical' if 'L3' in level_text else 'Vocational'))
            cur.execute('SELECT id FROM trades WHERE name = ?', (trade_name,))
            trade_id = cur.fetchone()[0]
            
            # Parse levels
            levels = parse_levels(level_text)
            
            # Insert school-trade relationship
            cur.execute('''INSERT OR IGNORE INTO school_trades 
                          (school_id, trade_id, levels_offered, is_active)
                          VALUES (?, ?, ?, 1)''',
                       (school_id, trade_id, json.dumps(levels)))
    
    conn.commit()
    print(f"✅ Populated database successfully!")
    
    # Print statistics
    cur.execute('SELECT COUNT(*) FROM provinces')
    print(f"   Provinces: {cur.fetchone()[0]}")
    cur.execute('SELECT COUNT(*) FROM districts')
    print(f"   Districts: {cur.fetchone()[0]}")
    cur.execute('SELECT COUNT(*) FROM schools')
    print(f"   Schools: {cur.fetchone()[0]}")
    cur.execute('SELECT COUNT(*) FROM trades')
    print(f"   Trades: {cur.fetchone()[0]}")
    cur.execute('SELECT COUNT(*) FROM school_trades')
    print(f"   School-Trade relationships: {cur.fetchone()[0]}")

if __name__ == '__main__':
    import os
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_dir = os.path.join(base_dir, 'data')
    os.makedirs(db_dir, exist_ok=True)
    db_path = os.path.join(db_dir, 'exam_local.db')
    
    conn = init_database(db_path)
    populate_schools(conn)
    conn.close()
    print(f"\n✅ Database population complete! ({db_path})")
