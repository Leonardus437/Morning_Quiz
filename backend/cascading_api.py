"""
Cascading Dropdown API Endpoints
Province -> District -> School -> Trade -> Level
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import json

router = APIRouter(prefix="/api/hierarchy", tags=["hierarchy"])

def get_db():
    from core.database import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/provinces")
def get_provinces(db: Session = Depends(get_db)):
    """Get all provinces"""
    from sqlalchemy import text
    result = db.execute(text("SELECT id, name, code FROM provinces ORDER BY name"))
    return [{"id": row[0], "name": row[1], "code": row[2]} for row in result]

@router.get("/districts/{province_id}")
def get_districts_by_province(province_id: int, db: Session = Depends(get_db)):
    """Get districts by province ID"""
    from sqlalchemy import text
    result = db.execute(text("""
        SELECT d.id, d.name, d.code, COUNT(DISTINCT s.id) as school_count
        FROM districts d
        LEFT JOIN schools s ON d.id = s.district_id AND s.is_active = 1
        WHERE d.province_id = :province_id
        GROUP BY d.id, d.name, d.code
        ORDER BY d.name
    """), {"province_id": province_id})
    
    districts = []
    for row in result:
        districts.append({
            "id": row[0],
            "name": row[1],
            "code": row[2],
            "school_count": row[3],
            "enabled": row[3] > 0
        })
    return districts

@router.get("/schools/{district_id}")
def get_schools_by_district(district_id: int, db: Session = Depends(get_db)):
    """Get schools by district ID"""
    from sqlalchemy import text
    result = db.execute(text("""
        SELECT s.id, s.name, s.code, s.school_type, s.status, s.boarding_status,
               COUNT(DISTINCT st.trade_id) as trade_count
        FROM schools s
        LEFT JOIN school_trades st ON s.id = st.school_id AND st.is_active = 1
        WHERE s.district_id = :district_id AND s.is_active = 1
        GROUP BY s.id, s.name, s.code, s.school_type, s.status, s.boarding_status
        ORDER BY s.name
    """), {"district_id": district_id})
    
    schools = []
    for row in result:
        schools.append({
            "id": row[0],
            "name": row[1],
            "code": row[2],
            "school_type": row[3],
            "status": row[4],
            "boarding_status": row[5],
            "trade_count": row[6],
            "enabled": row[6] > 0
        })
    return schools

@router.get("/trades/{school_id}")
def get_trades_by_school(school_id: int, db: Session = Depends(get_db)):
    """Get trades offered by a school with levels"""
    from sqlalchemy import text
    result = db.execute(text("""
        SELECT t.id, t.name, t.code, t.category, st.levels_offered
        FROM trades t
        JOIN school_trades st ON t.id = st.trade_id
        WHERE st.school_id = :school_id AND st.is_active = 1
        ORDER BY t.name
    """), {"school_id": school_id})
    
    trades = []
    for row in result:
        levels_str = row[4]
        try:
            levels = json.loads(levels_str) if levels_str else []
        except:
            levels = []
        
        trades.append({
            "id": row[0],
            "name": row[1],
            "code": row[2],
            "category": row[3],
            "levels_offered": levels
        })
    return trades

@router.get("/levels/{school_id}/{trade_id}")
def get_levels_by_school_trade(school_id: int, trade_id: int, db: Session = Depends(get_db)):
    """Get levels offered for a specific trade at a school"""
    from sqlalchemy import text
    result = db.execute(text("""
        SELECT levels_offered
        FROM school_trades
        WHERE school_id = :school_id AND trade_id = :trade_id AND is_active = 1
    """), {"school_id": school_id, "trade_id": trade_id})
    
    row = result.fetchone()
    if not row:
        return []
    
    levels_str = row[0]
    try:
        levels = json.loads(levels_str) if levels_str else []
    except:
        levels = []
    
    return [{"value": level, "label": level} for level in levels]

@router.get("/validate")
def validate_selection(
    province_id: Optional[int] = None,
    district_id: Optional[int] = None,
    school_id: Optional[int] = None,
    trade_id: Optional[int] = None,
    level: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Validate a complete hierarchical selection"""
    from sqlalchemy import text
    
    errors = []
    data = {}
    
    # Validate province
    if province_id:
        result = db.execute(text("SELECT name FROM provinces WHERE id = :id"), {"id": province_id})
        row = result.fetchone()
        if row:
            data['province'] = row[0]
        else:
            errors.append("Invalid province")
    
    # Validate district
    if district_id:
        result = db.execute(text("""
            SELECT d.name, p.name as province_name
            FROM districts d
            JOIN provinces p ON d.province_id = p.id
            WHERE d.id = :id
        """), {"id": district_id})
        row = result.fetchone()
        if row:
            data['district'] = row[0]
            if not province_id:
                data['province'] = row[1]
        else:
            errors.append("Invalid district")
    
    # Validate school
    if school_id:
        result = db.execute(text("""
            SELECT s.name, s.school_type, d.name as district_name
            FROM schools s
            JOIN districts d ON s.district_id = d.id
            WHERE s.id = :id AND s.is_active = 1
        """), {"id": school_id})
        row = result.fetchone()
        if row:
            data['school'] = row[0]
            data['school_type'] = row[1]
            if not district_id:
                data['district'] = row[2]
        else:
            errors.append("Invalid school")
    
    # Validate trade
    if trade_id and school_id:
        result = db.execute(text("""
            SELECT t.name, t.category, st.levels_offered
            FROM trades t
            JOIN school_trades st ON t.id = st.trade_id
            WHERE t.id = :trade_id AND st.school_id = :school_id AND st.is_active = 1
        """), {"trade_id": trade_id, "school_id": school_id})
        row = result.fetchone()
        if row:
            data['trade'] = row[0]
            data['trade_category'] = row[1]
            try:
                levels_offered = json.loads(row[2]) if row[2] else []
            except:
                levels_offered = []
            
            # Validate level
            if level:
                if level in levels_offered:
                    data['level'] = level
                else:
                    errors.append(f"Level {level} not offered for this trade")
            
            data['levels_available'] = levels_offered
        else:
            errors.append("Trade not offered at this school")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "data": data
    }

@router.get("/search/schools")
def search_schools(q: str, db: Session = Depends(get_db)):
    """Search schools by name"""
    from sqlalchemy import text
    result = db.execute(text("""
        SELECT s.id, s.name, s.school_type, d.name as district, p.name as province
        FROM schools s
        JOIN districts d ON s.district_id = d.id
        JOIN provinces p ON d.province_id = p.id
        WHERE s.name LIKE :query AND s.is_active = 1
        ORDER BY s.name
        LIMIT 20
    """), {"query": f"%{q}%"})
    
    return [{
        "id": row[0],
        "name": row[1],
        "school_type": row[2],
        "district": row[3],
        "province": row[4]
    } for row in result]

@router.get("/stats")
def get_hierarchy_stats(db: Session = Depends(get_db)):
    """Get statistics about the school hierarchy"""
    from sqlalchemy import text
    
    stats = {}
    
    # Count provinces
    result = db.execute(text("SELECT COUNT(*) FROM provinces"))
    stats['provinces'] = result.fetchone()[0]
    
    # Count districts
    result = db.execute(text("SELECT COUNT(*) FROM districts"))
    stats['districts'] = result.fetchone()[0]
    
    # Count schools
    result = db.execute(text("SELECT COUNT(*) FROM schools WHERE is_active = 1"))
    stats['schools'] = result.fetchone()[0]
    
    # Count trades
    result = db.execute(text("SELECT COUNT(*) FROM trades"))
    stats['trades'] = result.fetchone()[0]
    
    # Schools by province
    result = db.execute(text("""
        SELECT p.name, COUNT(s.id) as count
        FROM provinces p
        LEFT JOIN schools s ON p.id = s.province_id AND s.is_active = 1
        GROUP BY p.name
        ORDER BY count DESC
    """))
    stats['schools_by_province'] = [{"province": row[0], "count": row[1]} for row in result]
    
    # Schools by type
    result = db.execute(text("""
        SELECT school_type, COUNT(*) as count
        FROM schools
        WHERE is_active = 1
        GROUP BY school_type
        ORDER BY count DESC
    """))
    stats['schools_by_type'] = [{"type": row[0], "count": row[1]} for row in result]
    
    # Top trades
    result = db.execute(text("""
        SELECT t.name, COUNT(DISTINCT st.school_id) as school_count
        FROM trades t
        JOIN school_trades st ON t.id = st.trade_id
        WHERE st.is_active = 1
        GROUP BY t.name
        ORDER BY school_count DESC
        LIMIT 10
    """))
    stats['top_trades'] = [{"trade": row[0], "schools": row[1]} for row in result]
    
    return stats
