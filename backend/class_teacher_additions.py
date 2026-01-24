# Class Teacher System - Code to add to main.py

# 1. ADD THIS MODEL AFTER TeacherLesson class (around line 200)
"""
class ClassTeacher(Base):
    __tablename__ = "class_teachers"
    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("users.id"))
    department = Column(String(100))
    level = Column(String(50))
    assigned_at = Column(DateTime, default=datetime.utcnow)
"""

# 2. UPDATE ChatRoom model - ADD module_id column (around line 210)
"""
class ChatRoom(Base):
    __tablename__ = "chat_rooms"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    room_type = Column(String(50))
    department = Column(String(100))
    level = Column(String(50))
    module_id = Column(Integer, ForeignKey("lessons.id"))  # ADD THIS LINE
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
"""

# 3. ADD THESE ENDPOINTS BEFORE @app.on_event("startup") (around line 2100)
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

# 4. ADD MIGRATION in startup event (around line 2150)
"""
# Add this line in the migration section:
db.execute(text("ALTER TABLE chat_rooms ADD COLUMN IF NOT EXISTS module_id INTEGER"))
"""
