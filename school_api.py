"""
School Management API Endpoints
Handles provinces, districts, schools, and trades management
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
import json

router = APIRouter()

# Pydantic models
class Province(BaseModel):
    id: Optional[int] = None
    name: str
    code: str

class District(BaseModel):
    id: Optional[int] = None
    name: str
    code: str
    province_id: int
    province_name: Optional[str] = None

class SchoolType(BaseModel):
    id: Optional[int] = None
    name: str
    abbreviation: str
    description: Optional[str] = None

class Trade(BaseModel):
    id: Optional[int] = None
    name: str
    code: str
    category: Optional[str] = None
    description: Optional[str] = None

class School(BaseModel):
    id: Optional[int] = None
    name: str
    code: str
    school_type_id: int
    district_id: int
    province_id: int
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    is_reaccredited: bool = False
    accreditation_year: Optional[str] = None
    status: str = 'active'

class SchoolTrade(BaseModel):
    school_id: int
    trade_id: int
    levels: List[str]
    capacity: Optional[int] = None
    is_active: bool = True

class SchoolDetail(BaseModel):
    id: int
    name: str
    code: str
    school_type: str
    district: str
    province: str
    address: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    is_reaccredited: bool
    accreditation_year: Optional[str]
    status: str
    trades: List[dict]

# Database connection helper
def get_db_connection():
    import os
    return psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        database=os.getenv('DB_NAME', 'quiz_db'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'postgres')
    )

# ============ PROVINCES ============
@router.get("/provinces", response_model=List[Province])
async def get_provinces():
    """Get all provinces"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM provinces ORDER BY name")
    provinces = cur.fetchall()
    cur.close()
    conn.close()
    return provinces

@router.post("/provinces", response_model=Province)
async def create_province(province: Province):
    """Create a new province"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute(
            "INSERT INTO provinces (name, code) VALUES (%s, %s) RETURNING *",
            (province.name, province.code)
        )
        new_province = cur.fetchone()
        conn.commit()
        return new_province
    except psycopg2.IntegrityError:
        conn.rollback()
        raise HTTPException(status_code=400, detail="Province already exists")
    finally:
        cur.close()
        conn.close()

# ============ DISTRICTS ============
@router.get("/districts", response_model=List[District])
async def get_districts(province_id: Optional[int] = None):
    """Get all districts, optionally filtered by province"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    if province_id:
        cur.execute("""
            SELECT d.*, p.name as province_name 
            FROM districts d 
            JOIN provinces p ON d.province_id = p.id 
            WHERE d.province_id = %s 
            ORDER BY d.name
        """, (province_id,))
    else:
        cur.execute("""
            SELECT d.*, p.name as province_name 
            FROM districts d 
            JOIN provinces p ON d.province_id = p.id 
            ORDER BY p.name, d.name
        """)
    
    districts = cur.fetchall()
    cur.close()
    conn.close()
    return districts

@router.post("/districts", response_model=District)
async def create_district(district: District):
    """Create a new district"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute(
            "INSERT INTO districts (name, code, province_id) VALUES (%s, %s, %s) RETURNING *",
            (district.name, district.code, district.province_id)
        )
        new_district = cur.fetchone()
        conn.commit()
        return new_district
    except psycopg2.IntegrityError:
        conn.rollback()
        raise HTTPException(status_code=400, detail="District already exists in this province")
    finally:
        cur.close()
        conn.close()

# ============ SCHOOL TYPES ============
@router.get("/school-types", response_model=List[SchoolType])
async def get_school_types():
    """Get all school types"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM school_types ORDER BY name")
    types = cur.fetchall()
    cur.close()
    conn.close()
    return types

# ============ TRADES ============
@router.get("/trades", response_model=List[Trade])
async def get_trades(category: Optional[str] = None):
    """Get all trades, optionally filtered by category"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    if category:
        cur.execute("SELECT * FROM trades WHERE category = %s ORDER BY name", (category,))
    else:
        cur.execute("SELECT * FROM trades ORDER BY category, name")
    
    trades = cur.fetchall()
    cur.close()
    conn.close()
    return trades

@router.post("/trades", response_model=Trade)
async def create_trade(trade: Trade):
    """Create a new trade"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute(
            "INSERT INTO trades (name, code, category, description) VALUES (%s, %s, %s, %s) RETURNING *",
            (trade.name, trade.code, trade.category, trade.description)
        )
        new_trade = cur.fetchone()
        conn.commit()
        return new_trade
    except psycopg2.IntegrityError:
        conn.rollback()
        raise HTTPException(status_code=400, detail="Trade code already exists")
    finally:
        cur.close()
        conn.close()

# ============ SCHOOLS ============
@router.get("/schools", response_model=List[SchoolDetail])
async def get_schools(
    province_id: Optional[int] = None,
    district_id: Optional[int] = None,
    school_type_id: Optional[int] = None,
    is_reaccredited: Optional[bool] = None,
    trade_id: Optional[int] = None
):
    """Get all schools with filters"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    query = """
        SELECT 
            s.id, s.name, s.code, s.address, s.phone, s.email,
            s.is_reaccredited, s.accreditation_year, s.status,
            st.name as school_type,
            d.name as district,
            p.name as province
        FROM schools s
        JOIN school_types st ON s.school_type_id = st.id
        JOIN districts d ON s.district_id = d.id
        JOIN provinces p ON s.province_id = p.id
        WHERE 1=1
    """
    params = []
    
    if province_id:
        query += " AND s.province_id = %s"
        params.append(province_id)
    if district_id:
        query += " AND s.district_id = %s"
        params.append(district_id)
    if school_type_id:
        query += " AND s.school_type_id = %s"
        params.append(school_type_id)
    if is_reaccredited is not None:
        query += " AND s.is_reaccredited = %s"
        params.append(is_reaccredited)
    if trade_id:
        query += """ AND s.id IN (
            SELECT school_id FROM school_trades WHERE trade_id = %s
        )"""
        params.append(trade_id)
    
    query += " ORDER BY p.name, d.name, s.name"
    
    cur.execute(query, params)
    schools = cur.fetchall()
    
    # Get trades for each school
    for school in schools:
        cur.execute("""
            SELECT t.id, t.name, t.code, t.category, 
                   st.levels, st.capacity, st.is_active
            FROM school_trades st
            JOIN trades t ON st.trade_id = t.id
            WHERE st.school_id = %s AND st.is_active = true
            ORDER BY t.name
        """, (school['id'],))
        school['trades'] = cur.fetchall()
    
    cur.close()
    conn.close()
    return schools

@router.get("/schools/{school_id}", response_model=SchoolDetail)
async def get_school(school_id: int):
    """Get a specific school by ID"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute("""
        SELECT 
            s.id, s.name, s.code, s.address, s.phone, s.email,
            s.is_reaccredited, s.accreditation_year, s.status,
            st.name as school_type,
            d.name as district,
            p.name as province
        FROM schools s
        JOIN school_types st ON s.school_type_id = st.id
        JOIN districts d ON s.district_id = d.id
        JOIN provinces p ON s.province_id = p.id
        WHERE s.id = %s
    """, (school_id,))
    
    school = cur.fetchone()
    if not school:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="School not found")
    
    # Get trades
    cur.execute("""
        SELECT t.id, t.name, t.code, t.category, 
               st.levels, st.capacity, st.is_active
        FROM school_trades st
        JOIN trades t ON st.trade_id = t.id
        WHERE st.school_id = %s
        ORDER BY t.name
    """, (school_id,))
    school['trades'] = cur.fetchall()
    
    cur.close()
    conn.close()
    return school

@router.post("/schools", response_model=School)
async def create_school(school: School):
    """Create a new school"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("""
            INSERT INTO schools 
            (name, code, school_type_id, district_id, province_id, 
             address, phone, email, is_reaccredited, accreditation_year, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING *
        """, (
            school.name, school.code, school.school_type_id, 
            school.district_id, school.province_id, school.address,
            school.phone, school.email, school.is_reaccredited,
            school.accreditation_year, school.status
        ))
        new_school = cur.fetchone()
        conn.commit()
        return new_school
    except psycopg2.IntegrityError:
        conn.rollback()
        raise HTTPException(status_code=400, detail="School code already exists")
    finally:
        cur.close()
        conn.close()

@router.put("/schools/{school_id}", response_model=School)
async def update_school(school_id: int, school: School):
    """Update a school"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("""
            UPDATE schools SET
                name = %s, code = %s, school_type_id = %s,
                district_id = %s, province_id = %s, address = %s,
                phone = %s, email = %s, is_reaccredited = %s,
                accreditation_year = %s, status = %s
            WHERE id = %s
            RETURNING *
        """, (
            school.name, school.code, school.school_type_id,
            school.district_id, school.province_id, school.address,
            school.phone, school.email, school.is_reaccredited,
            school.accreditation_year, school.status, school_id
        ))
        updated_school = cur.fetchone()
        if not updated_school:
            raise HTTPException(status_code=404, detail="School not found")
        conn.commit()
        return updated_school
    finally:
        cur.close()
        conn.close()

@router.delete("/schools/{school_id}")
async def delete_school(school_id: int):
    """Delete a school"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM schools WHERE id = %s RETURNING id", (school_id,))
    deleted = cur.fetchone()
    if not deleted:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="School not found")
    conn.commit()
    cur.close()
    conn.close()
    return {"message": "School deleted successfully"}

# ============ SCHOOL TRADES ============
@router.post("/schools/{school_id}/trades")
async def add_school_trade(school_id: int, school_trade: SchoolTrade):
    """Add a trade to a school"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("""
            INSERT INTO school_trades 
            (school_id, trade_id, levels, capacity, is_active)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING *
        """, (
            school_id, school_trade.trade_id, 
            json.dumps(school_trade.levels),
            school_trade.capacity, school_trade.is_active
        ))
        new_school_trade = cur.fetchone()
        conn.commit()
        return new_school_trade
    except psycopg2.IntegrityError:
        conn.rollback()
        raise HTTPException(status_code=400, detail="Trade already assigned to this school")
    finally:
        cur.close()
        conn.close()

@router.delete("/schools/{school_id}/trades/{trade_id}")
async def remove_school_trade(school_id: int, trade_id: int):
    """Remove a trade from a school"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM school_trades WHERE school_id = %s AND trade_id = %s RETURNING id",
        (school_id, trade_id)
    )
    deleted = cur.fetchone()
    if not deleted:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="School trade not found")
    conn.commit()
    cur.close()
    conn.close()
    return {"message": "Trade removed from school successfully"}

# ============ SEARCH & STATISTICS ============
@router.get("/schools/search")
async def search_schools(q: str):
    """Search schools by name or code"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute("""
        SELECT 
            s.id, s.name, s.code,
            st.name as school_type,
            d.name as district,
            p.name as province
        FROM schools s
        JOIN school_types st ON s.school_type_id = st.id
        JOIN districts d ON s.district_id = d.id
        JOIN provinces p ON s.province_id = p.id
        WHERE s.name ILIKE %s OR s.code ILIKE %s
        ORDER BY s.name
        LIMIT 50
    """, (f'%{q}%', f'%{q}%'))
    
    results = cur.fetchall()
    cur.close()
    conn.close()
    return results

@router.get("/statistics")
async def get_statistics():
    """Get school system statistics"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    stats = {}
    
    # Total schools
    cur.execute("SELECT COUNT(*) as total FROM schools")
    stats['total_schools'] = cur.fetchone()['total']
    
    # Schools by province
    cur.execute("""
        SELECT p.name, COUNT(s.id) as count
        FROM provinces p
        LEFT JOIN schools s ON p.id = s.province_id
        GROUP BY p.name
        ORDER BY count DESC
    """)
    stats['schools_by_province'] = cur.fetchall()
    
    # Schools by type
    cur.execute("""
        SELECT st.name, COUNT(s.id) as count
        FROM school_types st
        LEFT JOIN schools s ON st.id = s.school_type_id
        GROUP BY st.name
        ORDER BY count DESC
    """)
    stats['schools_by_type'] = cur.fetchall()
    
    # Reaccredited vs non-reaccredited
    cur.execute("""
        SELECT 
            SUM(CASE WHEN is_reaccredited THEN 1 ELSE 0 END) as reaccredited,
            SUM(CASE WHEN NOT is_reaccredited THEN 1 ELSE 0 END) as non_reaccredited
        FROM schools
    """)
    stats['accreditation_status'] = cur.fetchone()
    
    # Most common trades
    cur.execute("""
        SELECT t.name, COUNT(st.id) as school_count
        FROM trades t
        JOIN school_trades st ON t.id = st.trade_id
        GROUP BY t.name
        ORDER BY school_count DESC
        LIMIT 10
    """)
    stats['top_trades'] = cur.fetchall()
    
    cur.close()
    conn.close()
    return stats
