#!/usr/bin/env python3
"""
Populate PostgreSQL database with hierarchical school data from CSV
"""

import os
import csv
import re
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://quiz_user:quiz_pass123@localhost:5432/morning_quiz")

PROVINCE_DISTRICTS = {
    'KIGALI CITY': ['GASABO', 'KICUKIRO', 'NYARUGENGE'],
    'EASTERN PROVINCE': ['BUGESERA', 'GATSIBO', 'KAYONZA', 'KIREHE', 'NGOMA', 'RWAMAGANA', 'NYAGATARE'],
    'NORTHERN PROVINCE': ['BURERA', 'GAKENKE', 'GICUMBI', 'MUSANZE', 'RULINDO'],
    'SOUTHERN PROVINCE': ['GISAGARA', 'HUYE', 'KAMONYI', 'MUHANGA', 'NYAMAGABE', 'NYANZA', 'NYARUGURU', 'RUHANGO'],
    'WESTERN PROVINCE': ['KARONGI', 'NGORORERO', 'NYABIHU', 'NYAMASHEKE', 'RUBAVU', 'RUSIZI', 'RUTSIRO']
}

def get_district_province(district):
    for province, districts in PROVINCE_DISTRICTS.items():
        if district.upper() in districts:
            return province
    return None

def extract_level_from_trade(trade_str):
    match = re.search(r'L(\d+)(?:-(\d+))?', trade_str)
    if match:
        if match.group(2):
            return f"L{match.group(1)}-{match.group(2)}"
        return f"L{match.group(1)}"
    return 'L3-5'

def clean_trade_name(trade_str):
    return re.sub(r'\s*L\d+(?:-\d+)?\s*$', '', trade_str).strip()

def populate():
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    db = Session()
    
    print("="*70)
    print("POPULATING POSTGRESQL DATABASE")
    print("="*70)
    
    try:
        # 1. Insert Provinces
        print("\n1. Inserting Provinces...")
        province_ids = {}
        for province in PROVINCE_DISTRICTS.keys():
            result = db.execute(text("""
                INSERT INTO provinces (name, code) 
                VALUES (:name, :code) 
                ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name
                RETURNING id
            """), {"name": province, "code": province[:3].upper()})
            province_ids[province] = result.fetchone()[0]
        db.commit()
        print(f"   ✓ {len(province_ids)} provinces")
        
        # 2. Insert Districts
        print("\n2. Inserting Districts...")
        district_ids = {}
        for province, districts in PROVINCE_DISTRICTS.items():
            for district in districts:
                # Try to get existing first
                result = db.execute(text("SELECT id FROM districts WHERE name = :name"), {"name": district})
                row = result.fetchone()
                if row:
                    district_ids[district] = row[0]
                else:
                    # Insert new
                    result = db.execute(text("""
                        INSERT INTO districts (province_id, name, code) 
                        VALUES (:pid, :name, :code)
                        RETURNING id
                    """), {"pid": province_ids[province], "name": district, "code": district[:3].upper()})
                    district_ids[district] = result.fetchone()[0]
        db.commit()
        print(f"   ✓ {len(district_ids)} districts")
        
        # 3. Read CSV and insert schools
        print("\n3. Inserting Schools...")
        csv_path = '/home/leo/Documents/Morning_Quiz/schools_final.csv'
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            schools_data = list(reader)
        
        school_ids = {}
        for school in schools_data:
            district = school['District'].strip().upper()
            if district not in district_ids:
                continue
            
            school_name = school['School_Name'].strip()
            school_type = school['Type'].strip()
            status = school['Status'].strip()
            boarding = school['Boarding'].strip()
            
            # Try to get existing first
            result = db.execute(text("SELECT id FROM schools WHERE name = :name AND district_id = :did"), 
                              {"name": school_name, "did": district_ids[district]})
            row = result.fetchone()
            if row:
                school_ids[school_name] = row[0]
            else:
                # Insert new
                result = db.execute(text("""
                    INSERT INTO schools (district_id, name, school_type, is_active)
                    VALUES (:did, :name, :type, true)
                    RETURNING id
                """), {"did": district_ids[district], "name": school_name, "type": school_type})
                school_ids[school_name] = result.fetchone()[0]
        
        db.commit()
        print(f"   ✓ {len(school_ids)} schools")
        
        # 4. Insert Trades and School-Trade relationships
        print("\n4. Inserting Trades and Relationships...")
        trade_ids = {}
        relationship_count = 0
        
        for school in schools_data:
            school_name = school['School_Name'].strip()
            if school_name not in school_ids:
                continue
            
            school_id = school_ids[school_name]
            trades_str = school.get('Accredited_Trades', '')
            
            if trades_str and trades_str != 'None':
                trades = [t.strip() for t in trades_str.split('|')]
                
                for trade_full in trades:
                    if not trade_full or len(trade_full) < 3:
                        continue
                    
                    level_str = extract_level_from_trade(trade_full)
                    trade_name = clean_trade_name(trade_full)
                    
                    # Insert trade
                    if trade_name not in trade_ids:
                        # Try to get existing first
                        result = db.execute(text("SELECT id FROM trades WHERE name = :name"), {"name": trade_name})
                        row = result.fetchone()
                        if row:
                            trade_ids[trade_name] = row[0]
                        else:
                            # Insert new
                            result = db.execute(text("""
                                INSERT INTO trades (name, code)
                                VALUES (:name, :code)
                                RETURNING id
                            """), {"name": trade_name, "code": trade_name[:10].upper().replace(' ', '_')})
                            trade_ids[trade_name] = result.fetchone()[0]
                    
                    if trade_name in trade_ids:
                        # Check if relationship exists
                        result = db.execute(text("""
                            SELECT id FROM school_trades 
                            WHERE school_id = :sid AND trade_id = :tid
                        """), {"sid": school_id, "tid": trade_ids[trade_name]})
                        if not result.fetchone():
                            # Insert school-trade relationship with levels
                            levels = [level_str] if level_str else ['L3-5']
                            db.execute(text("""
                                INSERT INTO school_trades (school_id, trade_id, levels_offered, is_active)
                                VALUES (:sid, :tid, :levels::json, true)
                            """), {"sid": school_id, "tid": trade_ids[trade_name], "levels": str(levels).replace("'", '"')})
                            relationship_count += 1
        
        db.commit()
        print(f"   ✓ {len(trade_ids)} trades")
        print(f"   ✓ {relationship_count} relationships")
        
        # Print stats
        print("\n" + "="*70)
        print("DATABASE POPULATION COMPLETE")
        print("="*70)
        
        result = db.execute(text("SELECT COUNT(*) FROM provinces"))
        print(f"Provinces: {result.fetchone()[0]}")
        
        result = db.execute(text("SELECT COUNT(*) FROM districts"))
        print(f"Districts: {result.fetchone()[0]}")
        
        result = db.execute(text("SELECT COUNT(*) FROM schools"))
        print(f"Schools: {result.fetchone()[0]}")
        
        result = db.execute(text("SELECT COUNT(*) FROM trades"))
        print(f"Trades: {result.fetchone()[0]}")
        
        result = db.execute(text("SELECT COUNT(*) FROM school_trades"))
        print(f"School-Trade Relationships: {result.fetchone()[0]}")
        
        print("\n✅ Database populated successfully!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    populate()
