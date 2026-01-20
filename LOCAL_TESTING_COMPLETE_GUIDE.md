# 🧪 LOCAL TESTING GUIDE - COMPLETE WORKFLOW

## 🎯 Goal
Test everything locally with Docker before deploying to production.

---

## ⚡ QUICK START (5 Steps)

### Step 1: Start Docker System
```cmd
SETUP_DOCKER_NOW.bat
```
Wait 5-10 minutes for build to complete.

### Step 2: Verify Containers Running
```cmd
docker-compose ps
```
All 3 containers should show "Up" status.

### Step 3: Run Automated Tests
Open in browser:
```
TEST_LOCAL_SYSTEM.html
```
All tests should pass ✅

### Step 4: Manual Testing
Open: http://localhost:3000
Login and test features (see checklist below)

### Step 5: Ready for Deployment
If all tests pass, system is ready for production!

---

## 📋 COMPLETE TEST CHECKLIST

### ✅ Phase 1: System Startup (5 minutes)

**1.1 Docker Containers**
```cmd
docker-compose ps
```
Expected:
```
NAME                    STATUS
tvet_quiz-backend-1     Up
tvet_quiz-db-1          Up  
tvet_quiz-frontend-1    Up
```

**1.2 Backend Health**
```cmd
curl http://localhost:8000/health
```
Expected: `{"status":"healthy"}`

**1.3 Frontend Access**
Open: http://localhost:3000
Expected: Login page loads

**1.4 API Documentation**
Open: http://localhost:8000/docs
Expected: Swagger UI loads

---

### ✅ Phase 2: Authentication (5 minutes)

**2.1 Admin Login**
- URL: http://localhost:3000
- Username: `admin`
- Password: `admin123`
- Expected: DOS Dashboard loads

**2.2 Teacher Login**
- Open new incognito window
- Username: `teacher001`
- Password: `teacher123`
- Expected: Teacher Dashboard loads

**2.3 Student Login**
- Open another incognito window
- Username: `student001`
- Password: `pass123`
- Expected: Student Dashboard loads

---

### ✅ Phase 3: Admin Features (10 minutes)

**3.1 View Students**
- Login as admin
- Click "Students" in sidebar
- Expected: Student list page loads

**3.2 Upload Students**
- Go to Students → Upload Students
- Select department: "Software Development"
- Select level: "Level 5"
- Upload test Excel file
- Expected: Students uploaded successfully

**3.3 Generate Credentials**
- Select department and level
- Click "Generate Credentials PDF"
- Expected: PDF downloads with usernames/passwords

**3.4 Register Teacher**
- Go to Teachers → Register Teacher
- Fill form:
  - Username: `teacher002`
  - Password: `teacher123`
  - Full Name: `Test Teacher`
  - Departments: Software Development
- Click "Register"
- Expected: Teacher created successfully

**3.5 Create Lesson**
- Go to Lessons → Create Lesson
- Fill form:
  - Title: `Test Lesson`
  - Code: `TEST101`
  - Department: Software Development
  - Level: Level 5
- Click "Create"
- Expected: Lesson created

**3.6 Assign Lesson to Teacher**
- Go to Lessons → Assign
- Select teacher002
- Select Test Lesson
- Click "Assign"
- Expected: Assignment successful

---

### ✅ Phase 4: Teacher Features (15 minutes)

**4.1 View Assigned Lessons**
- Login as teacher001
- Go to "My Courses"
- Expected: See assigned lessons

**4.2 Create Questions**
- Go to Questions → Create Question
- Create 5 questions:
  1. MCQ: "What is 2+2?" Options: [2,3,4,5] Answer: 4
  2. True/False: "Python is a programming language?" Answer: True
  3. Short Answer: "What is the capital of Rwanda?" Answer: Kigali
  4. Fill Blanks: "The sky is ___" Answer: blue
  5. Code Analysis: "What does print() do?" Answer: Outputs text
- Expected: All questions created

**4.3 Upload Questions (Bulk)**
- Go to Questions → Upload Questions
- Create test.txt with:
  ```
  What is HTML? HyperText Markup Language
  What is CSS? Cascading Style Sheets
  What is JS? JavaScript
  ```
- Upload file
- Expected: 3 questions imported

**4.4 Create Quiz**
- Go to Quizzes → Create Quiz
- Fill form:
  - Title: `Test Quiz 1`
  - Description: `Testing quiz system`
  - Duration: 10 minutes
  - Department: Software Development
  - Level: Level 5
- Select 5 questions
- Click "Create"
- Expected: Quiz created

**4.5 Broadcast Quiz**
- Go to Quizzes
- Find "Test Quiz 1"
- Click "Broadcast"
- Expected: Quiz becomes active, countdown starts

**4.6 View Quiz Status**
- Refresh quizzes page
- Expected: See countdown timer running

---

### ✅ Phase 5: Student Features (10 minutes)

**5.1 View Available Quizzes**
- Login as student001
- Go to "Available Quizzes"
- Expected: See "Test Quiz 1"

**5.2 Start Quiz**
- Click on "Test Quiz 1"
- Click "Start Quiz"
- Expected: Questions load

**5.3 Answer Questions**
- Answer all 5 questions
- Expected: Can select/type answers

**5.4 Submit Quiz**
- Click "Submit Quiz"
- Expected: Score displayed

**5.5 View Results**
- Go to "My Results"
- Expected: See quiz result with score

**5.6 View Leaderboard**
- Go to "Leaderboard"
- Expected: See ranking

---

### ✅ Phase 6: Results & Export (5 minutes)

**6.1 Teacher Views Results**
- Login as teacher001
- Go to Results
- Select "Test Quiz 1"
- Expected: See student submissions

**6.2 View Leaderboard**
- Click "Leaderboard"
- Expected: See ranked students

**6.3 Export PDF**
- Click "Export PDF"
- Expected: PDF downloads with results

**6.4 Export Excel**
- Click "Export Excel"
- Expected: Excel file downloads

---

### ✅ Phase 7: Advanced Features (10 minutes)

**7.1 Quiz Expiration**
- Wait for quiz timer to expire
- Try to access quiz as student
- Expected: "Quiz expired" message

**7.2 Rebroadcast Quiz**
- Login as teacher
- Click "Rebroadcast" on expired quiz
- Expected: Quiz active again with new timer

**7.3 Prevent Duplicate Submission**
- Student who already submitted tries again
- Expected: "Already submitted" message

**7.4 Multiple Students**
- Create 2 more student accounts
- Have them take the same quiz
- Expected: All submissions recorded

**7.5 Delete Quiz**
- Teacher deletes a quiz
- Expected: Quiz removed from list

**7.6 Clear Questions**
- Teacher clears all questions
- Expected: Question bank empty

---

### ✅ Phase 8: Data Persistence (5 minutes)

**8.1 Stop and Restart**
```cmd
docker-compose down
docker-compose up -d
```
Wait 1 minute, then:
- Login as admin
- Expected: All data still present

**8.2 Verify Data Retained**
- Check students still exist
- Check quizzes still exist
- Check results still exist
- Expected: All data persisted

---

### ✅ Phase 9: Performance Test (5 minutes)

**9.1 Multiple Concurrent Users**
- Open 5 browser windows
- Login as different students
- All take quiz simultaneously
- Expected: No errors, all submissions work

**9.2 Large File Upload**
- Upload Excel with 50 students
- Expected: All imported successfully

**9.3 Many Questions**
- Create quiz with 20 questions
- Expected: Loads and works fine

---

### ✅ Phase 10: Error Handling (5 minutes)

**10.1 Wrong Credentials**
- Try login with wrong password
- Expected: "Invalid credentials" error

**10.2 Expired Token**
- Login, wait 24 hours (or change token expiry)
- Try to access protected route
- Expected: Redirect to login

**10.3 Network Interruption**
- Start quiz, disconnect network
- Try to submit
- Expected: Graceful error message

**10.4 Invalid File Upload**
- Try to upload .exe file as students
- Expected: "Invalid file format" error

---

## 🎯 AUTOMATED TEST SCRIPT

Run this for quick verification:

```cmd
# Start system
docker-compose up -d

# Wait for startup
timeout /t 30

# Open test page
start TEST_LOCAL_SYSTEM.html

# Check logs
docker-compose logs --tail=50
```

---

## 📊 SUCCESS CRITERIA

### All Tests Must Pass:
- ✅ All 3 containers running
- ✅ Backend health check passes
- ✅ Frontend loads correctly
- ✅ All 3 user types can login
- ✅ Admin can upload students
- ✅ Admin can register teachers
- ✅ Teacher can create questions
- ✅ Teacher can create quiz
- ✅ Teacher can broadcast quiz
- ✅ Student can take quiz
- ✅ Student can submit quiz
- ✅ Results display correctly
- ✅ Exports work (PDF/Excel)
- ✅ Data persists after restart
- ✅ No console errors
- ✅ No backend errors in logs

---

## 🐛 TROUBLESHOOTING

### Backend Not Responding
```cmd
docker-compose logs backend
docker-compose restart backend
```

### Frontend Not Loading
```cmd
docker-compose logs frontend
docker-compose restart frontend
```

### Database Errors
```cmd
docker-compose logs db
docker-compose restart db
timeout /t 10
docker-compose restart backend
```

### Port Conflicts
```cmd
docker-compose down
netstat -ano | findstr :3000
netstat -ano | findstr :8000
# Kill processes, then restart
docker-compose up -d
```

---

## 📝 TEST REPORT TEMPLATE

After testing, fill this out:

```
LOCAL TESTING REPORT
Date: ___________
Tester: ___________

SYSTEM STARTUP
[ ] Containers running: ___/3
[ ] Backend health: PASS/FAIL
[ ] Frontend loads: PASS/FAIL

AUTHENTICATION
[ ] Admin login: PASS/FAIL
[ ] Teacher login: PASS/FAIL
[ ] Student login: PASS/FAIL

ADMIN FEATURES
[ ] Upload students: PASS/FAIL
[ ] Register teacher: PASS/FAIL
[ ] Create lesson: PASS/FAIL

TEACHER FEATURES
[ ] Create questions: PASS/FAIL
[ ] Create quiz: PASS/FAIL
[ ] Broadcast quiz: PASS/FAIL

STUDENT FEATURES
[ ] View quizzes: PASS/FAIL
[ ] Take quiz: PASS/FAIL
[ ] Submit quiz: PASS/FAIL

RESULTS & EXPORT
[ ] View results: PASS/FAIL
[ ] Export PDF: PASS/FAIL
[ ] Export Excel: PASS/FAIL

DATA PERSISTENCE
[ ] Data retained after restart: PASS/FAIL

OVERALL STATUS: READY/NOT READY

Issues Found:
1. ___________
2. ___________
3. ___________

Notes:
___________
```

---

## ✅ DEPLOYMENT READINESS

**System is ready for production when:**
- ✅ All automated tests pass
- ✅ All manual tests pass
- ✅ No errors in logs
- ✅ Performance is acceptable
- ✅ Data persists correctly
- ✅ All features work as expected

**Then proceed to:**
1. Push code to GitHub
2. Deploy backend to Render
3. Deploy frontend to Cloudflare
4. Test production deployment
5. Go live!

---

**Start Testing Now:** Run `SETUP_DOCKER_NOW.bat` then open `TEST_LOCAL_SYSTEM.html`
