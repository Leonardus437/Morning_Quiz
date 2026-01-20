"""
Complete Excel Upload Endpoint with Credential Generation
Add this to main.py
"""

@app.post("/admin/upload-students-excel")
async def upload_students_excel(
    file: UploadFile = File(...),
    department: str = Form(...),
    level: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload Excel file and generate credentials based on firstname + number"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Only Excel files (.xlsx, .xls) are supported")
    
    try:
        import xlrd
        import re
        from collections import defaultdict
        
        content = await file.read()
        
        # Read Excel file
        wb = xlrd.open_workbook(file_contents=content)
        sheet = wb.sheet_by_index(0)
        
        # Find where student names start (look for "Names" header)
        start_row = 0
        for i in range(min(20, sheet.nrows)):
            cell_value = str(sheet.cell_value(i, 0)).strip().lower()
            if 's/n' in cell_value or 'sn' in cell_value:
                start_row = i + 1
                break
        
        # Extract student names
        students = []
        for i in range(start_row, sheet.nrows):
            try:
                name = str(sheet.cell_value(i, 1)).strip()
                if name and name != 'Names' and len(name) > 2:
                    students.append(name)
            except:
                continue
        
        if not students:
            raise HTTPException(status_code=400, detail="No student names found in Excel file")
        
        # Generate usernames: firstname + incremented number
        firstname_counts = defaultdict(int)
        credentials = []
        created_count = 0
        updated_count = 0
        
        for full_name in students:
            try:
                # Extract first name
                name_parts = full_name.split()
                firstname = name_parts[0].lower() if name_parts else full_name.lower()
                # Clean firstname (remove special chars)
                firstname = re.sub(r'[^a-z]', '', firstname)
                
                # Increment counter for this firstname
                firstname_counts[firstname] += 1
                username = f"{firstname}{firstname_counts[firstname]}"
                
                # Default password
                password = "student123"
                password_hash = hashlib.sha256(password.encode()).hexdigest()
                
                # Check if user exists
                existing = db.query(User).filter(User.username == username).first()
                
                if existing:
                    existing.full_name = full_name
                    existing.department = department
                    existing.level = level
                    existing.password_hash = password_hash
                    updated_count += 1
                else:
                    new_student = User(
                        username=username,
                        password_hash=password_hash,
                        role='student',
                        full_name=full_name,
                        department=department,
                        level=level
                    )
                    db.add(new_student)
                    created_count += 1
                
                credentials.append({
                    'full_name': full_name,
                    'username': username,
                    'password': password,
                    'department': department,
                    'level': level
                })
                
            except Exception as e:
                print(f"Error processing {full_name}: {str(e)}")
                continue
        
        db.commit()
        
        return {
            'success': True,
            'message': f'Successfully imported {len(credentials)} students',
            'created': created_count,
            'updated': updated_count,
            'total': len(credentials),
            'credentials': credentials,
            'department': department,
            'level': level
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f'Import failed: {str(e)}')
