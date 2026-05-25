# Add these endpoints to main.py

# Hierarchical Login and Data Endpoints

@app.get("/hierarchy/provinces")
def get_provinces(db: Session = Depends(get_db)):
    """Get all provinces"""
    from sqlalchemy import text
    result = db.execute(text("SELECT id, name, code FROM provinces ORDER BY name"))
    return [{"id": row[0], "name": row[1], "code": row[2]} for row in result]

@app.get("/hierarchy/districts")
def get_districts(province_id: int, db: Session = Depends(get_db)):
    """Get districts by province with enabled/disabled status"""
    from sqlalchemy import text
    
    # Get all districts for the province with school count
    result = db.execute(text("""
        SELECT d.id, d.name, d.code, COUNT(s.id) as school_count
        FROM districts d
        LEFT JOIN schools s ON d.id = s.district_id AND s.is_active = true
        WHERE d.province_id = :pid
        GROUP BY d.id, d.name, d.code
        ORDER BY d.name
    """), {"pid": province_id})
    
    districts = []
    for row in result:
        districts.append({
            "id": row[0],
            "name": row[1],
            "code": row[2],
            "school_count": row[3],
            "enabled": row[3] > 0,  # Enabled only if has schools
            "disabled": row[3] == 0  # Disabled if no schools
        })
    
    return districts

@app.get("/hierarchy/schools")
def get_schools(district_id: int, db: Session = Depends(get_db)):
    """Get schools by district"""
    from sqlalchemy import text
    result = db.execute(text("SELECT id, name, code, school_type FROM schools WHERE district_id = :did AND is_active = true ORDER BY name"), {"did": district_id})
    return [{"id": row[0], "name": row[1], "code": row[2], "school_type": row[3]} for row in result]

@app.get("/hierarchy/school-trades")
def get_school_trades(school_id: int, db: Session = Depends(get_db)):
    """Get trades offered by a school with levels"""
    from sqlalchemy import text
    result = db.execute(text("""
        SELECT t.id, t.name, t.code, t.category, st.levels_offered
        FROM trades t
        JOIN school_trades st ON t.id = st.trade_id
        WHERE st.school_id = :sid AND st.is_active = true
        ORDER BY t.name
    """), {"sid": school_id})
    
    trades = []
    for row in result:
        import json
        levels = json.loads(row[4]) if isinstance(row[4], str) else row[4]
        trades.append({
            "id": row[0],
            "name": row[1],
            "code": row[2],
            "category": row[3],
            "levels_offered": levels
        })
    return trades

@app.post("/auth/hierarchical-login")
def hierarchical_login(data: Dict, db: Session = Depends(get_db)):
    """Login with hierarchical school/trade/level selection"""
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    school_id = data.get('school_id')
    trade_id = data.get('trade_id')
    level = data.get('level')
    
    # Authenticate user
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    if not verify_password_simple(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    # Update user's school/trade/level
    if school_id:
        user.school_id = school_id
    if trade_id:
        user.trade_id = trade_id
    if level:
        user.level = level
    
    db.commit()
    db.refresh(user)
    
    # Create access token
    access_token = create_access_token(data={"sub": user.username, "role": user.role})
    
    # Get school and trade names
    from sqlalchemy import text
    school_name = None
    trade_name = None
    
    if user.school_id:
        school_result = db.execute(text("SELECT name FROM schools WHERE id = :sid"), {"sid": user.school_id}).first()
        school_name = school_result[0] if school_result else None
    
    if user.trade_id:
        trade_result = db.execute(text("SELECT name FROM trades WHERE id = :tid"), {"tid": user.trade_id}).first()
        trade_name = trade_result[0] if trade_result else None
    
    user_dict = {
        "id": user.id,
        "username": user.username,
        "role": user.role,
        "full_name": user.full_name or "",
        "school_id": user.school_id,
        "school_name": school_name,
        "trade_id": user.trade_id,
        "trade_name": trade_name,
        "level": user.level,
        "department": user.department,  # Legacy
        "departments": user.departments or [],  # Legacy
        "is_class_teacher": bool(getattr(user, 'is_class_teacher', False))
    }
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_dict
    }

# Admin endpoints for managing hierarchy

@app.post("/admin/schools")
def create_school(school_data: Dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Create a new school (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can create schools")
    
    from sqlalchemy import text
    db.execute(text("""
        INSERT INTO schools (name, code, province_id, district_id, sector, school_type, is_active)
        VALUES (:name, :code, :province_id, :district_id, :sector, :school_type, true)
    """), school_data)
    db.commit()
    
    return {"message": "School created successfully"}

@app.post("/admin/trades")
def create_trade(trade_data: Dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Create a new trade (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can create trades")
    
    from sqlalchemy import text
    db.execute(text("""
        INSERT INTO trades (name, code, category, description)
        VALUES (:name, :code, :category, :description)
    """), trade_data)
    db.commit()
    
    return {"message": "Trade created successfully"}

@app.post("/admin/school-trades")
def assign_trade_to_school(data: Dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Assign a trade to a school with levels (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can assign trades")
    
    import json
    from sqlalchemy import text
    
    levels_json = json.dumps(data['levels_offered'])
    
    db.execute(text("""
        INSERT INTO school_trades (school_id, trade_id, levels_offered, is_active)
        VALUES (:school_id, :trade_id, :levels_offered, true)
    """), {
        "school_id": data['school_id'],
        "trade_id": data['trade_id'],
        "levels_offered": levels_json
    })
    db.commit()
    
    return {"message": "Trade assigned to school successfully"}

@app.get("/admin/schools/all")
def get_all_schools(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all schools with details (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can view all schools")
    
    from sqlalchemy import text
    result = db.execute(text("""
        SELECT s.id, s.name, s.code, s.school_type, s.sector,
               p.name as province_name, d.name as district_name
        FROM schools s
        JOIN provinces p ON s.province_id = p.id
        JOIN districts d ON s.district_id = d.id
        WHERE s.is_active = true
        ORDER BY p.name, d.name, s.name
    """))
    
    schools = []
    for row in result:
        schools.append({
            "id": row[0],
            "name": row[1],
            "code": row[2],
            "school_type": row[3],
            "sector": row[4],
            "province": row[5],
            "district": row[6]
        })
    
    return schools

@app.get("/admin/trades/all")
def get_all_trades(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all trades (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can view all trades")
    
    from sqlalchemy import text
    result = db.execute(text("SELECT id, name, code, category FROM trades ORDER BY category, name"))
    
    return [{"id": row[0], "name": row[1], "code": row[2], "category": row[3]} for row in result]
