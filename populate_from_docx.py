#!/usr/bin/env python3
"""
Parse DOCX file and populate school trades directly
"""

import os
import re
from docx import Document
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://quiz_user:quiz_pass123@db:5432/morning_quiz")

PROVINCE_DISTRICTS = {
    'KIGALI CITY': ['GASABO', 'KICUKIRO', 'NYARUGENGE'],
    'EASTERN PROVINCE': ['BUGESERA', 'GATSIBO', 'KAYONZA', 'KIREHE', 'NGOMA', 'RWAMAGANA', 'NYAGATARE'],
    'NORTHERN PROVINCE': ['BURERA', 'GAKENKE', 'GICUMBI', 'MUSANZE', 'RULINDO'],
    'SOUTHERN PROVINCE': ['GISAGARA', 'HUYE', 'KAMONYI', 'MUHANGA', 'NYAMAGABE', 'NYANZA', 'NYARUGURU', 'RUHANGO'],
    'WESTERN PROVINCE': ['KARONGI', 'NGORORERO', 'NYABIHU', 'NYAMASHEKE', 'RUBAVU', 'RUSIZI', 'RUTSIRO']
}

def extract_level_from_trade(trade_str):
    match = re.search(r'L(\d+)(?:-(\d+))?', trade_str)
    if match:
        if match.group(2):
            return f"L{match.group(1)}-{match.group(2)}"
        return f"L{match.group(1)}"
    return 'L3-5'

def clean_trade_name(trade_str):
    return re.sub(r'\s*L\d+(?:-\d+)?\s*$', '', trade_str).strip()

def parse_docx(docx_path):
    """Parse DOCX and extract school data"""
    doc = Document(docx_path)
    schools = []
    
    # Find the table
    for table in doc.tables:
        if len(table.rows) < 2:
            continue
        
        # Check if this is the schools table
        header_row = table.rows[0]
        headers = [cell.text.strip() for cell in header_row.cells]
        
        if 'District' not in ' '.join(headers):
            continue
        
        # Parse data rows
        for row in table.rows[1:]:
            cells = [cell.text.strip() for cell in row.cells]
            if len(cells) < 7:
                continue
            
            try:
                school_data = {
                    'sn': cells[0],
                    'district': cells[1],
                    'school_name': cells[2],
                    'type': cells[3],
                    'status': cells[4],
                    'boarding': cells[5],
                    'trade_count': cells[6],
                    'accredited_trades': cells[7] if len(cells) > 7 else '',
                    'not_accredited': cells[8] if len(cells) > 8 else '',
                    'reasons': cells[9] if len(cells) > 9 else ''
                }
                
                if school_data['school_name'] and school_data['district']:
                    schools.append(school_data)
            except:
                continue
    
    return schools

def populate_from_docx():
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    db = Session()
    
    print("="*70)
    print("POPULATING FROM DOCX FILE")
    print("="*70)
    
    try:
        # Parse DOCX
        docx_path = '/app/LIST_OF_REACREDITTED_AND_NON_REACREDITED_TSS_AND_VTC_2024-2025_lJhq.docx'
        print(f"\n📄 Parsing DOCX file...")
        schools_data = parse_docx(docx_path)
        print(f"✅ Found {len(schools_data)} schools in DOCX")
        
        # Get district mapping
        district_ids = {}
        for province, districts in PROVINCE_DISTRICTS.items():
            for district in districts:
                # Try both uppercase and title case
                result = db.execute(text("SELECT id FROM districts WHERE UPPER(name) = :name"), {"name": district})
                row = result.fetchone()
                if row:
                    district_ids[district] = row[0]
        
        print(f"📍 Found {len(district_ids)} districts in database")
        
        # Process each school
        added_count = 0
        new_trades = 0
        schools_processed = 0
        
        for school in schools_data:
            district_raw = school['district'].strip()
            district = district_raw.upper()
            if district not in district_ids:
                # Try to find by partial match
                for key in district_ids.keys():
                    if key in district or district in key:
                        district = key
                        break
            
            if district not in district_ids:
                continue
            
            school_name = school['school_name'].strip()
            if not school_name:
                continue
            
            # Find or create school
            result = db.execute(text("""
                SELECT id FROM schools 
                WHERE name = :name AND district_id = :did
            """), {"name": school_name, "did": district_ids[district]})
            
            row = result.fetchone()
            if row:
                school_id = row[0]
            else:
                # Create school
                school_type = school.get('type', 'TSS').strip()
                result = db.execute(text("""
                    INSERT INTO schools (district_id, name, school_type, is_active)
                    VALUES (:did, :name, :type, true)
                    RETURNING id
                """), {"did": district_ids[district], "name": school_name, "type": school_type})
                school_id = result.fetchone()[0]
                print(f"  ➕ New school: {school_name}")
            
            schools_processed += 1
            trades_str = school.get('accredited_trades', '')
            
            if not trades_str or trades_str == 'None':
                continue
            
            # Split trades by | or newline
            trades = [t.strip() for t in re.split(r'[|\n]', trades_str)]
            
            for trade_full in trades:
                if not trade_full or len(trade_full) < 3:
                    continue
                
                level_str = extract_level_from_trade(trade_full)
                trade_name = clean_trade_name(trade_full)
                
                # Get or create trade
                result = db.execute(text("SELECT id FROM trades WHERE name = :name"), {"name": trade_name})
                row = result.fetchone()
                
                if row:
                    trade_id = row[0]
                else:
                    try:
                        result = db.execute(text("""
                            INSERT INTO trades (name, code)
                            VALUES (:name, :code)
                            RETURNING id
                        """), {"name": trade_name, "code": trade_name[:10].upper().replace(' ', '_')})
                        trade_id = result.fetchone()[0]
                        new_trades += 1
                    except Exception as e:
                        # Rollback and try to get it again
                        db.rollback()
                        result = db.execute(text("SELECT id FROM trades WHERE name = :name"), {"name": trade_name})
                        row = result.fetchone()
                        if row:
                            trade_id = row[0]
                        else:
                            print(f"  ⚠️  Could not insert trade: {trade_name}")
                            continue
                
                # Check if relationship exists
                result = db.execute(text("""
                    SELECT id FROM school_trades 
                    WHERE school_id = :sid AND trade_id = :tid
                """), {"sid": school_id, "tid": trade_id})
                
                if not result.fetchone():
                    # Add relationship
                    import json
                    levels = [level_str] if level_str else ['L3-5']
                    db.execute(text("""
                        INSERT INTO school_trades (school_id, trade_id, levels_offered, is_active)
                        VALUES (:sid, :tid, :levels::json, true)
                    """), {"sid": school_id, "tid": trade_id, "levels": json.dumps(levels)})
                    added_count += 1
        
        db.commit()
        
        print("\n" + "="*70)
        print("RESULTS")
        print("="*70)
        print(f"✅ Processed {schools_processed} schools")
        print(f"✅ Added {new_trades} new trades")
        print(f"✅ Added {added_count} school-trade relationships")
        
        # Show stats
        result = db.execute(text("SELECT COUNT(*) FROM trades"))
        print(f"\n📊 Total trades: {result.fetchone()[0]}")
        
        result = db.execute(text("SELECT COUNT(*) FROM school_trades"))
        print(f"📊 Total school-trade relationships: {result.fetchone()[0]}")
        
        result = db.execute(text("""
            SELECT COUNT(*) FROM schools s 
            WHERE NOT EXISTS (SELECT 1 FROM school_trades st WHERE st.school_id = s.id)
        """))
        print(f"⚠️  Schools with no trades: {result.fetchone()[0]}")
        
        print("\n✅ Database populated from DOCX successfully!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    populate_from_docx()
