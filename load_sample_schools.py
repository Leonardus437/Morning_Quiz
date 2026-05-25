"""
Quick School Data Loader - Add sample schools for testing
"""

import json
from sqlalchemy import text
from main import SessionLocal

def load_sample_schools():
    """Load sample schools for each district"""
    db = SessionLocal()
    
    try:
        print("🚀 Loading sample schools...")
        
        # Get district IDs
        districts = db.execute(text("SELECT id, name FROM districts")).fetchall()
        district_map = {name: id for id, name in districts}
        
        # Get province IDs
        provinces = db.execute(text("SELECT id, name FROM provinces")).fetchall()
        province_map = {name: id for id, name in provinces}
        
        # Get school type IDs
        school_types = db.execute(text("SELECT id, abbreviation FROM school_types")).fetchall()
        type_map = {abbr: id for id, abbr in school_types}
        
        # Get trade IDs
        trades = db.execute(text("SELECT id, code FROM trades")).fetchall()
        trade_map = {code: id for id, code in trades}
        
        # Sample schools for each district
        sample_schools = [
            ("Bugesera", "Eastern Province", "NELSON MANDELA TSS", "TSS", "Juru"),
            ("Bugesera", "Eastern Province", "GASORE VTC", "VTC", "Gasore"),
            ("Gatsibo", "Eastern Province", "GATSIBO TSS", "TSS", "Kabarore"),
            ("Kayonza", "Eastern Province", "KAYONZA TSS", "TSS", "Kayonza"),
            ("Gicumbi", "Northern Province", "GICUMBI TSS", "TSS", "Byumba"),
            ("Gakenke", "Northern Province", "GAKENKE TSS", "TSS", "Gakenke"),
            ("Burera", "Northern Province", "BURERA TSS", "TSS", "Cyeru"),
            ("Huye", "Southern Province", "HUYE TSS", "TSS", "Ngoma"),
            ("Gisagara", "Southern Province", "GISAGARA TSS", "TSS", "Save"),
            ("Kamonyi", "Southern Province", "KAMONYI TSS", "TSS", "Kamonyi"),
            ("Karongi", "Western Province", "KARONGI TSS", "TSS", "Bwishyura"),
            ("Kicukiro", "Kigali City", "KICUKIRO TSS", "TSS", "Kicukiro"),
            ("Gasabo", "Kigali City", "GASABO TSS", "TSS", "Remera"),
        ]
        
        schools_loaded = 0
        for district, province, name, school_type, sector in sample_schools:
            if district not in district_map or province not in province_map:
                continue
            
            code = name.replace(" ", "_").upper()[:20]
            
            result = db.execute(text("""
                INSERT INTO schools (name, code, school_type_id, district_id, province_id, sector, is_active)
                VALUES (:name, :code, :type_id, :dist_id, :prov_id, :sector, true)
                ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name
                RETURNING id
            """), {
                "name": name,
                "code": code,
                "type_id": type_map.get(school_type, type_map['TSS']),
                "dist_id": district_map[district],
                "prov_id": province_map[province],
                "sector": sector
            })
            
            school_id = result.fetchone()[0]
            schools_loaded += 1
            
            # Add trades to this school
            for trade_code in ["AUTO", "CARP", "ELEC", "HOST", "ICT"]:
                if trade_code in trade_map:
                    db.execute(text("""
                        INSERT INTO school_trades (school_id, trade_id, levels_offered, is_active)
                        VALUES (:sid, :tid, :levels, true)
                        ON CONFLICT DO NOTHING
                    """), {
                        "sid": school_id,
                        "tid": trade_map[trade_code],
                        "levels": json.dumps(["L3", "L4", "L5"])
                    })
        
        db.commit()
        
        # Verification
        schools_count = db.execute(text("SELECT COUNT(*) FROM schools")).fetchone()[0]
        links_count = db.execute(text("SELECT COUNT(*) FROM school_trades")).fetchone()[0]
        
        print(f"✅ Loaded {schools_loaded} sample schools")
        print(f"✅ Total schools in database: {schools_count}")
        print(f"✅ Total school-trade links: {links_count}")
        
        print("\n✅ Sample school data loaded successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    load_sample_schools()
