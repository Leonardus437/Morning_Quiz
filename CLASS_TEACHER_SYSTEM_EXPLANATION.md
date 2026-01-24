# Class Teacher System - Complete Explanation

## Current System (What We Have)

### Teacher Model
```python
class User(Base):
    departments = Column(JSON)  # List of departments teacher can teach
    is_class_teacher = Column(Boolean, default=False)  # Flag but not used properly
```

### Current Chat Room Logic
When creating "student-teacher" room:
```python
# Adds ALL teachers who have that department in their departments array
teachers = db.query(User).filter(User.role == "teacher").all()
for teacher in teachers:
    if teacher.departments and department in teacher.departments:
        # Add teacher to room
```

**Problem:** No distinction between:
- Class teachers (should be in ALL class rooms)
- Module teachers (should only be in their module rooms)

---

## What You Need (Proper System)

### 1. Class Teacher Assignment Table

**New Model Needed:**
```python
class ClassTeacher(Base):
    __tablename__ = "class_teachers"
    id = Column(Integer, primary_key=True)
    teacher_id = Column(Integer, ForeignKey("users.id"))
    department = Column(String(100))
    level = Column(String(50))
    assigned_at = Column(DateTime, default=datetime.utcnow)
```

**Purpose:** Track which teacher is class teacher for which Department + Level combination

**Example Data:**
- Teacher ID 5 → Software Development + Level 5
- Teacher ID 8 → Networking + Level 6

---

### 2. Admin Endpoints to Manage Class Teachers

**Assign Class Teacher:**
```python
@app.post("/admin/assign-class-teacher")
def assign_class_teacher(data: Dict, current_user: User, db: Session):
    # Check if already assigned
    existing = db.query(ClassTeacher).filter(
        ClassTeacher.department == data["department"],
        ClassTeacher.level == data["level"]
    ).first()
    
    if existing:
        # Update existing
        existing.teacher_id = data["teacher_id"]
    else:
        # Create new
        class_teacher = ClassTeacher(
            teacher_id=data["teacher_id"],
            department=data["department"],
            level=data["level"]
        )
        db.add(class_teacher)
    
    db.commit()
    return {"message": "Class teacher assigned"}
```

**Get Class Teachers:**
```python
@app.get("/admin/class-teachers")
def get_class_teachers(current_user: User, db: Session):
    assignments = db.query(ClassTeacher).all()
    result = []
    for assignment in assignments:
        teacher = db.query(User).filter(User.id == assignment.teacher_id).first()
        result.append({
            "teacher_id": teacher.id,
            "teacher_name": teacher.full_name,
            "department": assignment.department,
            "level": assignment.level
        })
    return result
```

---

### 3. Updated Chat Room Creation Logic

**For "student-teacher" rooms:**
```python
elif room_type == "student-teacher" and department and level:
    # Add all students
    students = db.query(User).filter(
        User.role == "student",
        User.department == department,
        User.level == level
    ).all()
    for student in students:
        participants_added.append(student)
    
    # Add CLASS TEACHER for this dept/level
    class_teacher_assignment = db.query(ClassTeacher).filter(
        ClassTeacher.department == department,
        ClassTeacher.level == level
    ).first()
    
    if class_teacher_assignment:
        class_teacher = db.query(User).filter(
            User.id == class_teacher_assignment.teacher_id
        ).first()
        if class_teacher:
            p = ChatParticipant(room_id=room.id, user_id=class_teacher.id)
            db.add(p)
            participants_added.append(class_teacher)
```

**For "module" rooms (NEW):**
```python
elif room_type == "module" and module_id:
    # Get the lesson/module
    lesson = db.query(Lesson).filter(Lesson.id == module_id).first()
    
    # Add students from that dept/level
    students = db.query(User).filter(
        User.role == "student",
        User.department == lesson.department,
        User.level == lesson.level
    ).all()
    for student in students:
        participants_added.append(student)
    
    # Add ONLY teachers assigned to this module
    teacher_assignments = db.query(TeacherLesson).filter(
        TeacherLesson.lesson_id == module_id
    ).all()
    
    for assignment in teacher_assignments:
        teacher = db.query(User).filter(User.id == assignment.teacher_id).first()
        if teacher:
            p = ChatParticipant(room_id=room.id, user_id=teacher.id)
            db.add(p)
            participants_added.append(teacher)
```

---

### 4. Teacher Permissions for Room Creation

**Current User Check:**
```python
@app.post("/chat/rooms")
def create_chat_room(data: Dict, current_user: User, db: Session):
    room_type = data.get("room_type")
    
    # Admin can create any room
    if current_user.role == "admin":
        # Allow all room types
        pass
    
    # Teacher restrictions
    elif current_user.role == "teacher":
        # Check if class teacher
        is_class_teacher = db.query(ClassTeacher).filter(
            ClassTeacher.teacher_id == current_user.id
        ).first()
        
        if is_class_teacher:
            # Class teacher can create:
            # - student-student (for their class)
            # - student-teacher (for their class)
            # - module (for their assigned modules)
            if room_type in ["student-student", "student-teacher"]:
                # Must be for their assigned class
                if (data["department"] != is_class_teacher.department or 
                    data["level"] != is_class_teacher.level):
                    raise HTTPException(403, "Can only create rooms for your assigned class")
        else:
            # Regular teacher can ONLY create module rooms
            if room_type != "module":
                raise HTTPException(403, "You can only create module-based rooms")
            
            # Must be for their assigned module
            teacher_modules = db.query(TeacherLesson).filter(
                TeacherLesson.teacher_id == current_user.id
            ).all()
            module_ids = [tm.lesson_id for tm in teacher_modules]
            
            if data.get("module_id") not in module_ids:
                raise HTTPException(403, "You can only create rooms for your assigned modules")
```

---

## Summary of Changes Needed

### Database:
1. ✅ Add `ClassTeacher` table
2. ✅ Add `module_id` column to `ChatRoom` table

### Backend Endpoints:
1. ✅ `/admin/assign-class-teacher` - Assign teacher as class teacher
2. ✅ `/admin/remove-class-teacher` - Remove class teacher assignment
3. ✅ `/admin/class-teachers` - List all class teacher assignments
4. ✅ Update `/chat/rooms` POST - Add permission checks
5. ✅ Update `/chat/rooms` POST - Fix participant logic

### Frontend:
1. ✅ Admin page: Add "Assign Class Teacher" section
2. ✅ Chat modal: Add "Module" room type option
3. ✅ Chat modal: Show module selector when "module" type selected

---

## How It Works After Implementation

### Scenario 1: Admin Creates Room
- Admin creates "Level 5 Software Dev Discussion" (student-teacher type)
- System adds:
  - All Level 5 Software Dev students
  - The class teacher assigned to Level 5 Software Dev
- Notifications sent to all

### Scenario 2: Class Teacher Creates Room
- Class teacher (assigned to Level 5 Software Dev) creates room
- Can create student-student or student-teacher rooms for Level 5 Software Dev
- Cannot create rooms for other classes

### Scenario 3: Module Teacher Creates Room
- Teacher assigned to "Database Management" module creates room
- Can ONLY create "module" type room
- System adds:
  - Students enrolled in that module (from lesson's dept/level)
  - Only teachers assigned to that specific module
- Cannot create general class rooms

---

## Benefits

1. **Clear Roles:**
   - Class teachers manage their class
   - Module teachers manage their modules
   - Admin manages everything

2. **Proper Notifications:**
   - Only relevant teachers get notified
   - Class teacher always in class discussions
   - Module teachers only in their module discussions

3. **Security:**
   - Teachers can't create rooms for classes they don't teach
   - Module teachers limited to their modules

4. **Scalability:**
   - Easy to assign/reassign class teachers
   - Clear audit trail of who teaches what
