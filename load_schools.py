"""
Load School Data into Database
Loads provinces, districts, schools, trades from JSON
"""

import json
from sqlalchemy import text
from main import SessionLocal

def load_school_data():
    """Load all school data from schools_final.json"""
    db = SessionLocal()
    
    try:
        print("🚀 Loading school data...")
        
        # Load JSON data
        with open('schools_final.json', 'r') as f:
            data = json.load(f)
        
        # 1. Load Provinces
        print("📍 Loading provinces...")
        provinces = {
            "Eastern Province": "EP",
            "Western Province": "WP",
            "Northern Province": "NP",
            "Southern Province": "SP",
            "Kigali City": "KC"
        }
        
        province_ids = {}
        for name, code in provinces.items():
            result = db.execute(text("""
                INSERT INTO provinces (name, code)
                VALUES (:name, :code)
                ON CONFLICT DO NOTHING
                RETURNING id
            """), {"name": name, "code": code})
            db.commit()
            
            # Get province ID
            prov = db.execute(text("SELECT id FROM provinces WHERE code = :code"), {"code": code}).fetchone()
            if prov:
                province_ids[name] = prov[0]
        
        print(f"✅ Loaded {len(province_ids)} provinces")
        
        # 2. Load Districts
        print("🏘️ Loading districts...")
        district_ids = {}
        districts_data = [
            ("Bugesera", "BUG", "Eastern Province"),
            ("Gatsibo", "GAT", "Eastern Province"),
            ("Kayonza", "KAY", "Eastern Province"),
            ("Gicumbi", "GIC", "Northern Province"),
            ("Gakenke", "GAK", "Northern Province"),
            ("Burera", "BUR", "Northern Province"),
            ("Huye", "HUY", "Southern Province"),
            ("Gisagara", "GIS", "Southern Province"),
            ("Kamonyi", "KAM", "Southern Province"),
            ("Karongi", "KAR", "Western Province"),
            ("Kicukiro", "KCK", "Kigali City"),
            ("Gasabo", "GAS", "Kigali City")
        ]
        
        for name, code, province in districts_data:
            if province in province_ids:
                result = db.execute(text("""
                    INSERT INTO districts (name, code, province_id)
                    VALUES (:name, :code, :pid)
                    ON CONFLICT DO NOTHING
                    RETURNING id
                """), {"name": name, "code": code, "pid": province_ids[province]})
                db.commit()
                
                # Get district ID
                dist = db.execute(text("SELECT id FROM districts WHERE code = :code"), {"code": code}).fetchone()
                if dist:
                    district_ids[name] = dist[0]
        
        print(f"✅ Loaded {len(district_ids)} districts")
        
        # 3. Load School Types
        print("🏫 Loading school types...")
        school_types = [
            ("Technical Secondary School", "TSS", "TVET schools offering technical education"),
            ("Vocational Training Center", "VTC", "Centers for vocational skills training"),
            ("Integrated Polytechnic Regional Center", "IPRC", "Regional polytechnic centers")
        ]
        
        school_type_ids = {}
        for name, abbr, desc in school_types:
            result = db.execute(text("""
                INSERT INTO school_types (name, abbreviation, description)
                VALUES (:name, :abbr, :desc)
                ON CONFLICT (abbreviation) DO NOTHING
                RETURNING id
            """), {"name": name, "abbr": abbr, "desc": desc})
            db.commit()
            
            # Get school type ID
            st = db.execute(text("SELECT id FROM school_types WHERE abbreviation = :abbr"), {"abbr": abbr}).fetchone()
            if st:
                school_type_ids[abbr] = st[0]
        
        print(f"✅ Loaded {len(school_type_ids)} school types")
        
        # 4. Load Schools from JSON
        print("🏫 Loading schools from JSON...")
        schools_loaded = 0
        
        for school in data.get('schools', []):
            district_name = school.get('district')
            if district_name not in district_ids:
                continue
            
            province_name = school.get('province')
            if province_name not in province_ids:
                continue
            
            school_type = school.get('school_type', 'TSS')
            if school_type not in school_type_ids:
                school_type = 'TSS'
            
            result = db.execute(text("""
                INSERT INTO schools (name, code, school_type_id, district_id, province_id, sector, is_active)
                VALUES (:name, :code, :type_id, :dist_id, :prov_id, :sector, true)
                ON CONFLICT (code) DO NOTHING
                RETURNING id
            """), {
                "name": school.get('name'),
                "code": school.get('code', school.get('name')[:10].upper()),
                "type_id": school_type_ids[school_type],
                "dist_id": district_ids[district_name],
                "prov_id": province_ids[province_name],
                "sector": school.get('sector', '')
            })
            
            if result.rowcount > 0:
                schools_loaded += 1
        
        db.commit()
        print(f"✅ Loaded {schools_loaded} schools")
        
        # 5. Load Trades
        print("🔧 Loading trades...")
        trades_data = [
            ("Automotive Technology", "AUTO", "Automotive and Transport"),
            ("Carpentry", "CARP", "Construction and Woodwork"),
            ("Electrical Installation", "ELEC", "Electrical and Electronics"),
            ("Electronics", "ELTN", "Electrical and Electronics"),
            ("Hospitality", "HOST", "Hospitality and Tourism"),
            ("ICT", "ICT", "Information Technology"),
            ("Masonry", "MASO", "Construction and Woodwork"),
            ("Plumbing", "PLUM", "Construction and Woodwork"),
            ("Tailoring", "TAIL", "Fashion and Textiles"),
            ("Welding", "WELD", "Metal Work")
        ]
        
        trade_ids = {}
        for name, code, category in trades_data:
            result = db.execute(text("""
                INSERT INTO trades (name, code, category)
                VALUES (:name, :code, :cat)
                ON CONFLICT (code) DO NOTHING
                RETURNING id
            """), {"name": name, "code": code, "cat": category})
            db.commit()
            
            # Get trade ID
            trade = db.execute(text("SELECT id FROM trades WHERE code = :code"), {"code": code}).fetchone()
            if trade:
                trade_ids[code] = trade[0]
        
        print(f"✅ Loaded {len(trade_ids)} trades")
        
        # 6. Link Schools to Trades
        print("🔗 Linking schools to trades...")
        links_created = 0
        
        # Get all schools
        schools = db.execute(text("SELECT id, code FROM schools")).fetchall()
        
        # Assign common trades to all schools (simplified)
        common_trades = ["AUTO", "CARP", "ELEC", "HOST", "ICT"]
        
        for school_id, school_code in schools:
            for trade_code in common_trades:
                if trade_code in trade_ids:
                    db.execute(text("""
                        INSERT INTO school_trades (school_id, trade_id, levels_offered, is_active)
                        VALUES (:sid, :tid, :levels, true)
                        ON CONFLICT DO NOTHING
                    """), {
                        "sid": school_id,
                        "tid": trade_ids[trade_code],
                        "levels": json.dumps(["L3", "L4", "L5"])
                    })
                    links_created += 1
        
        db.commit()
        print(f"✅ Created {links_created} school-trade links")
        
        # Final verification
        print("\n📊 Final counts:")
        provinces_count = db.execute(text("SELECT COUNT(*) FROM provinces")).fetchone()[0]
        districts_count = db.execute(text("SELECT COUNT(*) FROM districts")).fetchone()[0]
        schools_count = db.execute(text("SELECT COUNT(*) FROM schools")).fetchone()[0]
        trades_count = db.execute(text("SELECT COUNT(*) FROM trades")).fetchone()[0]
        links_count = db.execute(text("SELECT COUNT(*) FROM school_trades")).fetchone()[0]
        
        print(f"  Provinces: {provinces_count}")
        print(f"  Districts: {districts_count}")
        print(f"  Schools: {schools_count}")
        print(f"  Trades: {trades_count}")
        print(f"  School-Trade Links: {links_count}")
        
        print("\n✅ School data loaded successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error loading school data: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    load_school_data()
