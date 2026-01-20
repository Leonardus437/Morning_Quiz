# Comprehensive Admin Feature Testing Script
Write-Host "🧪 TESTING ALL ADMIN FEATURES..." -ForegroundColor Cyan

# Wait for backend
Start-Sleep -Seconds 5

# 1. Login as Admin
Write-Host "`n✅ TEST 1: Admin Login" -ForegroundColor Yellow
$loginResponse = Invoke-WebRequest -Uri 'http://localhost:8000/auth/login' -Method POST -Headers @{'Content-Type'='application/json'} -Body '{"username":"admin","password":"admin123"}'
$token = ($loginResponse.Content | ConvertFrom-Json).access_token
Write-Host "Token: $($token.Substring(0,20))..." -ForegroundColor Green

# 2. Get All Students
Write-Host "`n✅ TEST 2: Get All Students" -ForegroundColor Yellow
try {
    $students = Invoke-WebRequest -Uri 'http://localhost:8000/admin/students' -Headers @{'Authorization'="Bearer $token"}
    $studentsData = $students.Content | ConvertFrom-Json
    Write-Host "Total Students: $($studentsData.total)" -ForegroundColor Green
} catch {
    Write-Host "❌ FAILED: $_" -ForegroundColor Red
}

# 3. Upload New Student
Write-Host "`n✅ TEST 3: Upload Student" -ForegroundColor Yellow
try {
    $uploadBody = '{"students":[{"username":"verify_student","full_name":"Verification Student","department":"Software Development","level":"Level 3","password":"student123"}]}'
    $upload = Invoke-WebRequest -Uri 'http://localhost:8000/admin/upload-students' -Method POST -Headers @{'Authorization'="Bearer $token";'Content-Type'='application/json'} -Body $uploadBody
    Write-Host ($upload.Content | ConvertFrom-Json | ConvertTo-Json) -ForegroundColor Green
} catch {
    Write-Host "❌ FAILED: $_" -ForegroundColor Red
}

# 4. Get Lessons
Write-Host "`n✅ TEST 4: Get Lessons" -ForegroundColor Yellow
try {
    $lessons = Invoke-WebRequest -Uri 'http://localhost:8000/lessons' -Headers @{'Authorization'="Bearer $token"}
    $lessonsData = $lessons.Content | ConvertFrom-Json
    Write-Host "Total Lessons: $($lessonsData.Count)" -ForegroundColor Green
} catch {
    Write-Host "❌ FAILED: $_" -ForegroundColor Red
}

# 5. Create Lesson
Write-Host "`n✅ TEST 5: Create Lesson" -ForegroundColor Yellow
try {
    $lessonBody = '{"title":"Test Lesson","code":"TEST001","description":"Test","department":"Software Development","level":"Level 3","classification":"Core"}'
    $lesson = Invoke-WebRequest -Uri 'http://localhost:8000/lessons' -Method POST -Headers @{'Authorization'="Bearer $token";'Content-Type'='application/json'} -Body $lessonBody
    Write-Host "Lesson Created: $(($lesson.Content | ConvertFrom-Json).title)" -ForegroundColor Green
} catch {
    Write-Host "❌ FAILED: $_" -ForegroundColor Red
}

# 6. Get Teachers
Write-Host "`n✅ TEST 6: Get Teachers" -ForegroundColor Yellow
try {
    $teachers = Invoke-WebRequest -Uri 'http://localhost:8000/teachers' -Headers @{'Authorization'="Bearer $token"}
    $teachersData = $teachers.Content | ConvertFrom-Json
    Write-Host "Total Teachers: $($teachersData.Count)" -ForegroundColor Green
} catch {
    Write-Host "❌ FAILED: $_" -ForegroundColor Red
}

# 7. Register Teacher
Write-Host "`n✅ TEST 7: Register Teacher" -ForegroundColor Yellow
try {
    $teacherBody = '{"username":"test_teacher_verify","password":"test123","full_name":"Test Teacher Verify","departments":["Software Development"]}'
    $teacher = Invoke-WebRequest -Uri 'http://localhost:8000/admin/register-teacher' -Method POST -Headers @{'Authorization'="Bearer $token";'Content-Type'='application/json'} -Body $teacherBody
    Write-Host "Teacher Registered: $(($teacher.Content | ConvertFrom-Json).teacher.full_name)" -ForegroundColor Green
} catch {
    Write-Host "❌ FAILED: $_" -ForegroundColor Red
}

# 8. Assign Lesson to Teacher
Write-Host "`n✅ TEST 8: Assign Lesson to Teacher" -ForegroundColor Yellow
try {
    $assignBody = '{"teacher_id":2,"lesson_id":1}'
    $assign = Invoke-WebRequest -Uri 'http://localhost:8000/teacher-lessons' -Method POST -Headers @{'Authorization'="Bearer $token";'Content-Type'='application/json'} -Body $assignBody
    Write-Host ($assign.Content | ConvertFrom-Json).message -ForegroundColor Green
} catch {
    Write-Host "⚠️ May already be assigned" -ForegroundColor Yellow
}

# 9. Get Teacher Lessons
Write-Host "`n✅ TEST 9: Get Teacher Lessons" -ForegroundColor Yellow
try {
    $teacherLessons = Invoke-WebRequest -Uri 'http://localhost:8000/teacher-lessons/2' -Headers @{'Authorization'="Bearer $token"}
    $lessonsData = $teacherLessons.Content | ConvertFrom-Json
    Write-Host "Teacher has $($lessonsData.Count) lessons assigned" -ForegroundColor Green
} catch {
    Write-Host "❌ FAILED: $_" -ForegroundColor Red
}

# 10. Get Schedules
Write-Host "`n✅ TEST 10: Get Schedules" -ForegroundColor Yellow
try {
    $schedules = Invoke-WebRequest -Uri 'http://localhost:8000/schedules' -Headers @{'Authorization'="Bearer $token"}
    $schedulesData = $schedules.Content | ConvertFrom-Json
    Write-Host "Total Schedules: $($schedulesData.Count)" -ForegroundColor Green
} catch {
    Write-Host "❌ FAILED: $_" -ForegroundColor Red
}

# 11. Get Announcements
Write-Host "`n✅ TEST 11: Get Announcements" -ForegroundColor Yellow
try {
    $announcements = Invoke-WebRequest -Uri 'http://localhost:8000/announcements' -Headers @{'Authorization'="Bearer $token"}
    $announcementsData = $announcements.Content | ConvertFrom-Json
    Write-Host "Total Announcements: $($announcementsData.Count)" -ForegroundColor Green
} catch {
    Write-Host "❌ FAILED: $_" -ForegroundColor Red
}

Write-Host "`n🎉 ADMIN FEATURE TESTING COMPLETE!" -ForegroundColor Cyan
