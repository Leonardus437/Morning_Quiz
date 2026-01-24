# Class Teacher Management Endpoints

# Add these to main.py after the chat endpoints

"""
@app.post("/admin/assign-class-teacher")
def assign_class_teacher(data: Dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can assign class teachers")
    
    teacher_id = data.get("teacher_id")
    department = data.get("department")
    level = data.get("level")
    
    existing = db.query(ClassTeacher).filter(
        ClassTeacher.department == department,
        ClassTeacher.level == level
    ).first()
    
    if existing:
        existing.teacher_id = teacher_id
    else:
        class_teacher = ClassTeacher(
            teacher_id=teacher_id,
            department=department,
            level=level
        )
        db.add(class_teacher)
    
    db.commit()
    return {"message": "Class teacher assigned successfully"}

@app.get("/admin/class-teachers")
def get_class_teachers(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can view class teachers")
    
    assignments = db.query(ClassTeacher).all()
    result = []
    for assignment in assignments:
        teacher = db.query(User).filter(User.id == assignment.teacher_id).first()
        if teacher:
            result.append({
                "id": assignment.id,
                "teacher_id": teacher.id,
                "teacher_name": teacher.full_name,
                "department": assignment.department,
                "level": assignment.level,
                "assigned_at": assignment.assigned_at.isoformat()
            })
    return result

@app.delete("/admin/class-teacher/{assignment_id}")
def remove_class_teacher(assignment_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can remove class teachers")
    
    assignment = db.query(ClassTeacher).filter(ClassTeacher.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    db.delete(assignment)
    db.commit()
    return {"message": "Class teacher removed successfully"}
"""
