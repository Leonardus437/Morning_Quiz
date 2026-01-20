# 👨‍💼 Admin (DOS) Operations Guide

## Complete CRUD Operations Reference

---

## 📚 **LESSONS MANAGEMENT**

### ✅ Create Lesson
**Endpoint:** `POST /lessons`
```json
{
  "title": "Python Programming",
  "code": "SD401",
  "description": "Introduction to Python",
  "department": "Software Development",
  "level": "Level 4",
  "classification": "Core"
}
```

### 📖 Read Lessons
**Endpoint:** `GET /lessons`
**Filters:** `?department=Software Development&level=Level 4&include_inactive=false`

### ✏️ Update Lesson
**Endpoint:** `PUT /lessons/{lesson_id}`
```json
{
  "title": "Updated Title",
  "code": "SD401",
  "description": "Updated description",
  "department": "Software Development",
  "level": "Level 5",
  "classification": "Core"
}
```

### 🔄 Activate/Deactivate Lesson
**Activate:** `PUT /lessons/{lesson_id}/activate`
**Deactivate:** `PUT /lessons/{lesson_id}/deactivate`

### 🗑️ Delete Lesson
**Endpoint:** `DELETE /lessons/{lesson_id}`
**Note:** Cannot delete if lesson has questions or teacher assignments

---

## 👨‍🏫 **TEACHERS MANAGEMENT**

### ✅ Create Teacher
**Endpoint:** `POST /admin/register-teacher`
```json
{
  "username": "teacher001",
  "password": "pass123",
  "full_name": "John Smith",
  "departments": ["Software Development", "Computer System and Architecture"]
}
```

### 📖 Read Teachers
**Endpoint:** `GET /teachers`
**Filters:** `?department=Software Development&include_class_teachers=true`

### 📋 Get Teacher Details
**Endpoint:** `GET /teachers/{teacher_id}`
**Returns:** Full details including assigned lessons and class assignments

### ✏️ Update Teacher
**Endpoint:** `PUT /admin/teacher/{teacher_id}`
```json
{
  "full_name": "Updated Name",
  "departments": ["Software Development"]
}
```

### 🔑 Reset Teacher Password
**Endpoint:** `POST /admin/reset-teacher-password/{teacher_id}?new_password=newpass123`

### 🗑️ Delete Teacher
**Endpoint:** `DELETE /teachers/{teacher_id}`
**Note:** Cannot delete if teacher has questions or quizzes

---

## 👨‍🎓 **STUDENTS MANAGEMENT**

### ✅ Create Students (Bulk)
**Endpoint:** `POST /teacher/upload-students`
```json
{
  "students": [
    {
      "username": "student001",
      "full_name": "Alice Johnson",
      "department": "Software Development",
      "level": "Level 4",
      "password": "student123"
    }
  ]
}
```

### 📖 Read Students
**Endpoint:** `GET /admin/students`
**Filters:** `?department=Software Development&level=Level 4&search=Alice&limit=100&offset=0`

### 📋 Get Student Details
**Endpoint:** `GET /admin/students/{student_id}`
**Returns:** Full details including quiz history and statistics

### ✏️ Update Student
**Endpoint:** `PUT /admin/students/{student_id}`
```json
{
  "full_name": "Updated Name",
  "department": "Software Development",
  "level": "Level 5",
  "password": "newpass123"
}
```

### 🗑️ Delete Student
**Endpoint:** `DELETE /admin/students/{student_id}`
**Note:** Deletes all related quiz attempts and answers

### 🗑️ Clear All Students
**Endpoint:** `DELETE /admin/clear-all-students`
**Warning:** Deletes ALL students from system

---

## 🏢 **DEPARTMENTS & LEVELS**

### 📊 Get Departments with Statistics
**Endpoint:** `GET /admin/departments`
**Returns:**
```json
[
  {
    "name": "Software Development",
    "students_count": 45,
    "teachers_count": 5,
    "lessons_count": 12,
    "quizzes_count": 8
  }
]
```

### 📊 Get Levels with Statistics
**Endpoint:** `GET /admin/levels`
**Filters:** `?department=Software Development`
**Returns:**
```json
[
  {
    "name": "Level 4",
    "students_count": 30,
    "lessons_count": 8,
    "quizzes_count": 5
  }
]
```

### 📊 Get Overall Statistics
**Endpoint:** `GET /admin/statistics`
**Returns:**
```json
{
  "totals": {
    "students": 150,
    "teachers": 12,
    "lessons": 45,
    "quizzes": 30,
    "active_quizzes": 5,
    "questions": 500,
    "quiz_attempts": 1200
  },
  "recent_students": [...],
  "recent_quizzes": [...],
  "recent_attempts": [...]
}
```

---

## 🔗 **TEACHER-LESSON ASSIGNMENTS**

### ✅ Assign Lesson to Teacher
**Endpoint:** `POST /teacher-lessons`
```json
{
  "teacher_id": 5,
  "lesson_id": 12
}
```

### 📖 Get Teacher's Lessons
**Endpoint:** `GET /teacher-lessons/{teacher_id}`

### 🗑️ Remove Lesson Assignment
**Endpoint:** `DELETE /teacher-lessons/{assignment_id}`

---

## 🏫 **CLASS TEACHER ASSIGNMENTS**

### ✅ Assign Class Teacher
**Endpoint:** `POST /admin/assign-class-teacher`
```json
{
  "teacher_id": 5,
  "department": "Software Development",
  "level": "Level 4"
}
```

### 📖 Get All Class Teachers
**Endpoint:** `GET /admin/class-teachers`

---

## 📢 **ANNOUNCEMENTS**

### ✅ Create Announcement
**Endpoint:** `POST /announcements`
```json
{
  "title": "Important Notice",
  "content": "Quiz scheduled for tomorrow",
  "priority": "high",
  "departments": ["Software Development"],
  "levels": ["Level 4"]
}
```

### 📖 Get Announcements
**Endpoint:** `GET /announcements`

### 🔄 Deactivate Announcement
**Endpoint:** `PUT /announcements/{announcement_id}/deactivate`

---

## 📅 **SCHEDULES**

### ✅ Create Schedule
**Endpoint:** `POST /schedules`
```json
{
  "title": "Weekly Timetable",
  "description": "Week 1 schedule",
  "scheduled_date": "2024-01-15T08:00:00",
  "departments": ["Software Development"],
  "levels": ["Level 4"]
}
```

### 📤 Upload Schedule File
**Endpoint:** `POST /schedules/upload`
**Form Data:** `file` (PDF/DOCX), `title`, `description`

### 📖 Get Schedules
**Endpoint:** `GET /schedules`

### 📥 Download Schedule
**Endpoint:** `GET /schedules/{schedule_id}/download`

---

## 📊 **REPORTS & EXPORTS**

### 📄 Generate Student Credentials PDF
**Endpoint:** `POST /admin/generate-student-credentials/{department}/{level}`
**Example:** `POST /admin/generate-student-credentials/Software Development/Level 4`

### 📊 Download All Results (Excel)
**Endpoint:** `GET /admin/results/download/excel`

### 📊 Download All Results (PDF)
**Endpoint:** `GET /admin/results/download/pdf`

### 📊 Generate Department Report
**Endpoint:** `GET /admin/reports/department?department=Software Development&level=Level 4&reportType=monthly&date=2024-01`

### 📊 Generate Quiz Report
**Endpoint:** `GET /admin/quiz-reports/{report_type}?department=Software Development&level=Level 4`
**Types:** `daily`, `weekly`, `monthly`

---

## 🧪 **TESTING ADMIN OPERATIONS**

### Run Automated Tests
```cmd
# Start system
docker-compose up -d

# Run tests
test_admin.bat

# Or manually
python test_admin_crud.py
```

### Manual Testing Checklist
- [ ] Create lesson
- [ ] Update lesson
- [ ] Delete lesson
- [ ] Create teacher
- [ ] Assign lesson to teacher
- [ ] Update teacher
- [ ] Delete teacher
- [ ] Upload students
- [ ] Update student
- [ ] Delete student
- [ ] View statistics
- [ ] Generate reports

---

## ⚠️ **IMPORTANT NOTES**

### Data Integrity
- **Cannot delete lesson** with questions or assignments
- **Cannot delete teacher** with questions or quizzes
- **Deleting student** removes all quiz attempts
- **Always backup** before bulk deletions

### Best Practices
1. **Test on sample data** before production
2. **Use deactivate** instead of delete when possible
3. **Export reports** regularly for backup
4. **Verify assignments** before deleting teachers
5. **Check dependencies** before deletions

### Error Handling
- **400:** Bad request (validation error)
- **401:** Unauthorized (login required)
- **403:** Forbidden (admin access required)
- **404:** Not found
- **500:** Server error

---

## 🎯 **QUICK REFERENCE**

### Common Operations
```bash
# Login
POST /auth/login

# Get all students
GET /admin/students

# Get statistics
GET /admin/statistics

# Create lesson
POST /lessons

# Assign teacher
POST /teacher-lessons

# Generate report
GET /admin/quiz-reports/daily
```

### Access URLs
- **Admin Panel:** `http://localhost:3000/admin`
- **API Docs:** `http://localhost:8000/docs`
- **Health Check:** `http://localhost:8000/health`

---

## ✅ **VERIFICATION**

All CRUD operations are:
- ✅ **Fully implemented**
- ✅ **Properly validated**
- ✅ **Error handled**
- ✅ **Tested and working**
- ✅ **Offline-ready**
- ✅ **LAN accessible**

**System Status: PRODUCTION READY** 🎉
