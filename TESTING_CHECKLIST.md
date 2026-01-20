# Complete Testing Checklist - Morning Quiz System

## 🔍 Phase 1: System Health Check (5 minutes)

### 1.1 Check Container Status
```bash
docker-compose ps
```
**Expected Output:**
- ✅ `tvet_quiz-db-1` - UP
- ✅ `tvet_quiz-backend-1` - UP
- ✅ `tvet_quiz-frontend-1` - UP

### 1.2 Check Backend Logs
```bash
docker-compose logs backend --tail=20
```
**Look for:**
- ✅ "Database tables created successfully"
- ✅ "✅ Admin user created" or "Admin user already exists"
- ✅ "✅ Default teacher user created" or "Teacher already exists"
- ✅ "✅ Default student user created" or "Student already exists"
- ✅ No ERROR messages

### 1.3 Test API Health
Open browser and visit:
```
http://localhost:8000/health
```
**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-24T...",
  "service": "Morning Quiz API"
}
```

---

## 🔐 Phase 2: Authentication Testing (10 minutes)

### 2.1 Test Teacher Login
1. Go to: `http://localhost:3000/teacher`
2. Login with:
   - Username: `teacher001`
   - Password: `teacher123`
3. **Expected:** Dashboard loads with "👨🏫 Teacher Dashboard"

### 2.2 Test Student Login
1. Go to: `http://localhost:3000`
2. Login with:
   - Username: `student001`
   - Password: `pass123`
3. **Expected:** Student dashboard loads

### 2.3 Test Admin Login
1. Go to: `http://localhost:3000/admin`
2. Login with:
   - Username: `admin`
   - Password: `admin123`
3. **Expected:** Admin dashboard loads

---

## 📊 Phase 3: Debug Endpoints Check (5 minutes)

### 3.1 Check All Quizzes
```
http://localhost:8000/debug/quizzes
```
**Expected:** JSON showing all quizzes in system

### 3.2 Check All Students
```
http://localhost:8000/debug/students
```
**Expected:** JSON showing all students with their dept/level

---

## 🎯 Phase 4: Quiz Broadcast Test (15 minutes) - CRITICAL

### 4.1 Setup Test Data

**Step 1: Create a Test Student (as Admin)**
1. Login to Admin: `http://localhost:3000/admin`
2. Go to "👥 Students" tab
3. Click "📄 Upload Students"
4. Select Department: `Computer System and Architecture`
5. Select Level: `Level 3`
6. Add student manually:
   - Name: `Test Student One`
   - Click "➕ Add"
7. **Expected:** Alert shows "✅ Student added! Username: CSA3XXXX Password: student123"

**Step 2: Create a Test Quiz (as Teacher)**
1. Login to Teacher: `http://localhost:3000/teacher`
2. Go to "➕ Add Question" tab
3. Create a simple question:
   - Question: "What is 2+2?"
   - Type: Multiple Choice
   - Options: A) 4, B) 5, C) 6, D) 7
   - Correct Answer: 4
   - Department: `Computer System and Architecture`
   - Level: `Level 3`
   - Lesson: (select any available)
   - Points: 1
4. Click "🚀 Create Questions"
5. **Expected:** "✅ Successfully created 1 questions!"

**Step 3: Create Quiz**
1. Go to "🎯 Create Quiz" tab
2. Fill in:
   - Title: `Test Broadcast Quiz`
   - Description: `Testing broadcast functionality`
   - Department: `Computer System and Architecture`
   - Level: `Level 3`
   - Scheduled Time: (pick any future time)
   - Duration: 30 minutes
3. Select the question you just created
4. Click "🚀 Create Quiz"
5. **Expected:** "✅ Quiz created successfully!"

### 4.2 Broadcast Quiz (THE CRITICAL TEST)

**Step 1: Broadcast**
1. Go to "🎮 My Quizzes" tab
2. Find "Test Broadcast Quiz"
3. Click "📡 Broadcast Now"
4. **CRITICAL CHECK:** Alert should show:
   ```
   Quiz broadcasted to all students immediately! Students notified: 1
   ```
   - ✅ If you see "Students notified: 1" → BROADCAST WORKING ✅
   - ❌ If you see "Students notified: 0" → BROADCAST FAILED ❌

**Step 2: Check Backend Logs**
```bash
docker-compose logs backend --tail=30
```
**Look for this exact pattern:**
```
🎯 BROADCASTING QUIZ [ID]
   Quiz: Test Broadcast Quiz
   Department: Computer System and Architecture
   Level: Level 3
   Found 1 students to notify
   - Notifying: CSA3XXXX (Computer System and Architecture - Level 3)
   ✅ Quiz [ID] is now ACTIVE and BROADCASTING
```

### 4.3 Student Sees Quiz

**Step 1: Login as Test Student**
1. Logout from teacher
2. Go to: `http://localhost:3000`
3. Login with the student credentials from Step 4.1
   - Username: `CSA3XXXX` (from the alert)
   - Password: `student123`
4. **Expected:** Student dashboard loads

**Step 2: Check Available Quizzes**
1. Look for "AVAILABLE QUIZZES" section
2. **CRITICAL CHECK:** Should see "Test Broadcast Quiz"
   - ✅ If quiz appears → BROADCAST WORKING ✅
   - ❌ If quiz doesn't appear → BROADCAST FAILED ❌

**Step 3: Check Backend Logs for Student Fetch**
```bash
docker-compose logs backend --tail=30
```
**Look for:**
```
🔍 STUDENT QUIZ FETCH: CSA3XXXX
   Student Dept/Level: Computer System and Architecture - Level 3
   📊 Total ACTIVE quizzes in system: 1
      Quiz [ID]: 'Test Broadcast Quiz' | Dept: Computer System and Architecture | Level: Level 3
   ✅ Filtered quizzes for CSA3XXXX: 1 matches
      ✓ Quiz [ID]: 'Test Broadcast Quiz'
```

### 4.4 Student Takes Quiz

1. Click on "Test Broadcast Quiz"
2. **Expected:** Quiz loads with question
3. Select answer: "4"
4. Click "Submit"
5. **Expected:** Score shows "1/1" (100%)

---

## ✅ Phase 5: Verification Summary

### Success Criteria Checklist

- [ ] All 3 containers running (db, backend, frontend)
- [ ] Backend logs show no errors
- [ ] `/health` endpoint responds
- [ ] Teacher login works
- [ ] Student login works
- [ ] Admin login works
- [ ] `/debug/quizzes` shows data
- [ ] `/debug/students` shows data
- [ ] Test student created successfully
- [ ] Test question created successfully
- [ ] Test quiz created successfully
- [ ] **CRITICAL: Broadcast shows "Students notified: 1"**
- [ ] **CRITICAL: Backend logs show broadcast confirmation**
- [ ] **CRITICAL: Student sees quiz in AVAILABLE QUIZZES**
- [ ] **CRITICAL: Student can take quiz and submit**
- [ ] Backend logs show student quiz fetch with filtering

---

## 🐛 Troubleshooting Guide

### Issue: Containers not running
```bash
docker-compose up -d
docker-compose ps
```

### Issue: Backend errors
```bash
docker-compose logs backend --tail=50
docker-compose restart backend
```

### Issue: Database issues
```bash
docker-compose down -v
docker-compose up -d
```

### Issue: "Students notified: 0"
**Check:**
1. Student department/level matches quiz exactly
2. Student exists in database: `http://localhost:8000/debug/students`
3. Quiz department/level is correct: `http://localhost:8000/debug/quizzes`
4. Backend logs for mismatch errors

### Issue: Student doesn't see quiz
**Check:**
1. Quiz is active (is_active = true)
2. Student's dept/level matches quiz exactly
3. Student refreshed page
4. Check backend logs for filtering details

---

## 📝 Quick Command Reference

```bash
# View all containers
docker-compose ps

# View backend logs (last 50 lines)
docker-compose logs backend --tail=50

# View all logs
docker-compose logs --tail=50

# Restart backend
docker-compose restart backend

# Restart everything
docker-compose restart

# Stop everything
docker-compose down

# Start everything
docker-compose up -d

# Full rebuild
docker-compose down -v
docker-compose up -d --build
```

---

## 🎉 Expected Final State

When everything is working perfectly:

1. ✅ Teacher can create quizzes
2. ✅ Teacher can broadcast quizzes
3. ✅ Teacher sees "Students notified: X" alert
4. ✅ Backend logs show broadcast confirmation
5. ✅ Students see broadcasted quizzes
6. ✅ Students can take quizzes
7. ✅ Scores are recorded
8. ✅ No errors in logs

---

## 📞 Support

If any step fails:
1. Check backend logs: `docker-compose logs backend --tail=50`
2. Check debug endpoints
3. Verify department/level matches exactly
4. Restart backend: `docker-compose restart backend`
5. If still failing, do full rebuild: `docker-compose down -v && docker-compose up -d --build`
