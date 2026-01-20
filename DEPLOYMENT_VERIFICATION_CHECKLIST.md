# 🚀 DEPLOYMENT VERIFICATION CHECKLIST

## System Overview
- **Frontend**: Cloudflare Pages - https://tsskqizi.pages.dev
- **Backend**: Render - https://tvet-quiz-backend.onrender.com
- **Status**: Production Deployment

---

## ✅ STEP 1: BACKEND VERIFICATION (5 minutes)

### 1.1 Check Backend Health
Open in browser:
```
https://tvet-quiz-backend.onrender.com/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-XX...",
  "rwanda_time": "HH:MM:SS",
  "timezone": "CAT/EAT (UTC+2)",
  "service": "Morning Quiz API",
  "version": "1.8-SUBMISSION-FIX",
  "cors": "enabled"
}
```

✅ **Pass**: Backend is online and responding
❌ **Fail**: Backend is down or not responding (see troubleshooting)

### 1.2 Check API Documentation
Open:
```
https://tvet-quiz-backend.onrender.com/docs
```

**Expected**: FastAPI Swagger UI with all endpoints listed

✅ **Pass**: API docs load successfully
❌ **Fail**: 404 or error page

### 1.3 Test Authentication Endpoint
Using browser console or Postman:
```bash
curl -X POST "https://tvet-quiz-backend.onrender.com/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

**Expected Response:**
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "admin",
    "role": "admin",
    "full_name": "DOS Administrator"
  }
}
```

✅ **Pass**: Login successful with token
❌ **Fail**: 401 or connection error

---

## ✅ STEP 2: FRONTEND VERIFICATION (5 minutes)

### 2.1 Check Frontend Loads
Open in browser:
```
https://tsskqizi.pages.dev
```

**Expected**: Homepage loads with login form

✅ **Pass**: Page loads correctly
❌ **Fail**: 404, blank page, or error

### 2.2 Check API Connection
Open browser console (F12) and check for:
```
[API] Detecting hostname: tsskqizi.pages.dev
[API] Using Render backend for Cloudflare Pages
```

✅ **Pass**: Frontend detects Cloudflare and uses Render backend
❌ **Fail**: Wrong API URL or connection errors

### 2.3 Test Login Flow
1. Go to https://tsskqizi.pages.dev
2. Click "Login"
3. Enter credentials:
   - Username: `admin`
   - Password: `admin123`
4. Click "Login"

**Expected**: Redirect to DOS Dashboard

✅ **Pass**: Login successful, dashboard loads
❌ **Fail**: Login error or stuck on login page

---

## ✅ STEP 3: CORE FEATURES VERIFICATION (10 minutes)

### 3.1 DOS Admin Panel
**Login as**: admin / admin123

**Test Features:**
- [ ] Dashboard loads with statistics
- [ ] Can view all students
- [ ] Can view all teachers
- [ ] Can create new lesson
- [ ] Can register new teacher
- [ ] Can upload student list (Excel/PDF)
- [ ] Can generate student credentials PDF
- [ ] Can view all quizzes

### 3.2 Teacher Panel
**Login as**: teacher001 / teacher123

**Test Features:**
- [ ] Dashboard loads
- [ ] Can view assigned lessons
- [ ] Can create questions
- [ ] Can upload questions (TXT/PDF/DOCX)
- [ ] Can create quiz
- [ ] Can broadcast quiz
- [ ] Can view quiz results
- [ ] Can export results (PDF/Excel)
- [ ] Can view leaderboard

### 3.3 Student Panel
**Login as**: student001 / pass123

**Test Features:**
- [ ] Dashboard loads
- [ ] Can view available quizzes
- [ ] Can start quiz
- [ ] Can submit quiz
- [ ] Can view results
- [ ] Can see leaderboard

---

## ✅ STEP 4: CRITICAL WORKFLOWS (15 minutes)

### 4.1 Complete Quiz Workflow

**Step 1: Teacher Creates Quiz**
1. Login as teacher001
2. Go to "Questions" → "Create Question"
3. Add 3 questions (MCQ, True/False, Short Answer)
4. Go to "Quizzes" → "Create Quiz"
5. Select questions, set duration (5 minutes)
6. Click "Create Quiz"

✅ **Pass**: Quiz created successfully

**Step 2: Teacher Broadcasts Quiz**
1. Go to "Quizzes"
2. Click "Broadcast" on the quiz
3. Verify countdown starts

✅ **Pass**: Quiz is active and countdown running

**Step 3: Student Takes Quiz**
1. Login as student001 (new browser/incognito)
2. Go to "Available Quizzes"
3. Click on the quiz
4. Answer all questions
5. Click "Submit"

✅ **Pass**: Quiz submitted, score displayed

**Step 4: Teacher Views Results**
1. Back to teacher panel
2. Go to "Results"
3. View leaderboard
4. Export PDF
5. Export Excel

✅ **Pass**: Results visible, exports work

### 4.2 Student Management Workflow

**Step 1: Upload Students**
1. Login as admin
2. Go to "Students" → "Upload Students"
3. Select department and level
4. Upload Excel file with student names
5. Click "Upload"

✅ **Pass**: Students uploaded successfully

**Step 2: Generate Credentials**
1. Go to "Students"
2. Select department and level
3. Click "Generate Credentials PDF"
4. Download PDF

✅ **Pass**: PDF downloaded with usernames/passwords

**Step 3: Test Student Login**
1. Open PDF
2. Copy a student username/password
3. Login with those credentials
4. Verify student dashboard loads

✅ **Pass**: Student can login successfully

### 4.3 Teacher Management Workflow

**Step 1: Register Teacher**
1. Login as admin
2. Go to "Teachers" → "Register Teacher"
3. Fill in details:
   - Username: teacher002
   - Password: teacher123
   - Full Name: Test Teacher
   - Departments: Software Development
4. Click "Register"

✅ **Pass**: Teacher registered successfully

**Step 2: Assign Lesson**
1. Go to "Lessons" → "Assign to Teacher"
2. Select teacher002
3. Select a lesson
4. Click "Assign"

✅ **Pass**: Lesson assigned successfully

**Step 3: Test Teacher Login**
1. Logout
2. Login as teacher002 / teacher123
3. Verify assigned lesson appears in "My Courses"

✅ **Pass**: Teacher can see assigned lesson

---

## ✅ STEP 5: PERFORMANCE & RELIABILITY (5 minutes)

### 5.1 Cold Start Test
1. Wait 15 minutes (Render free tier spins down)
2. Open https://tsskqizi.pages.dev
3. Try to login

**Expected**: First request takes 30-60 seconds (cold start)

✅ **Pass**: System wakes up and works
❌ **Fail**: Timeout or error

### 5.2 Multiple Users Test
1. Open 3 browser windows (Chrome, Firefox, Edge)
2. Login as different users in each
3. Have teacher broadcast quiz
4. Have 2 students take quiz simultaneously

✅ **Pass**: All users can work concurrently
❌ **Fail**: Conflicts or errors

### 5.3 Mobile Test
1. Open https://tsskqizi.pages.dev on phone
2. Login as student
3. Take a quiz
4. Submit

✅ **Pass**: Mobile interface works smoothly
❌ **Fail**: Layout broken or unusable

---

## ✅ STEP 6: DATA PERSISTENCE (5 minutes)

### 6.1 Test Data Retention
1. Create a quiz as teacher
2. Logout
3. Wait 5 minutes
4. Login again
5. Verify quiz still exists

✅ **Pass**: Data persists across sessions
❌ **Fail**: Data lost

### 6.2 Test Database Integrity
1. Upload 10 students
2. Create 5 questions
3. Create 1 quiz
4. Have 3 students take quiz
5. Logout and login
6. Verify all data intact

✅ **Pass**: All data preserved
❌ **Fail**: Missing data

---

## 🔧 TROUBLESHOOTING

### Problem: Backend Not Responding

**Check 1: Render Service Status**
1. Go to https://dashboard.render.com
2. Login
3. Check "tvet-quiz-backend" status
4. If "Suspended", click "Resume"

**Check 2: Environment Variables**
1. Go to service → "Environment"
2. Verify all variables set:
   - DATABASE_URL
   - SECRET_KEY
   - OFFLINE_MODE=false
   - PYTHON_VERSION=3.11.0

**Check 3: Logs**
1. Go to service → "Logs"
2. Look for errors
3. Common issues:
   - Database connection failed
   - Module not found
   - Port binding error

**Fix: Redeploy**
```
Dashboard → Manual Deploy → Clear build cache & deploy
```

### Problem: Frontend Not Loading

**Check 1: Cloudflare Pages Status**
1. Go to https://dash.cloudflare.com
2. Check "tsskwizi" deployment status
3. Verify latest deployment succeeded

**Check 2: Build Logs**
1. Go to deployment → "View build log"
2. Look for errors
3. Common issues:
   - Build failed
   - Missing dependencies
   - Configuration error

**Fix: Redeploy**
1. Go to GitHub
2. Make a small change (add space to README)
3. Commit and push
4. Cloudflare auto-deploys

### Problem: Login Fails

**Check 1: CORS Error**
Open browser console, look for:
```
Access to fetch at 'https://tvet-quiz-backend.onrender.com' 
from origin 'https://tsskqizi.pages.dev' has been blocked by CORS
```

**Fix**: Backend already has CORS enabled, but verify:
1. Check backend logs
2. Ensure `allow_origins=["*"]` in main.py

**Check 2: Wrong Credentials**
Default accounts:
- Admin: admin / admin123
- Teacher: teacher001 / teacher123
- Student: student001 / pass123

**Check 3: Token Expiration**
1. Clear browser cache
2. Clear localStorage (F12 → Application → Local Storage → Clear)
3. Try login again

### Problem: Quiz Submission Fails

**Check 1: Backend Logs**
Look for:
```
Quiz submission error: ...
```

**Check 2: Network Tab**
1. Open F12 → Network
2. Submit quiz
3. Look for failed requests
4. Check response body

**Common Issues:**
- Token expired (re-login)
- Quiz already submitted
- Quiz time expired
- Network timeout

### Problem: File Upload Fails

**Check 1: File Format**
Supported formats:
- Students: .xlsx, .xls, .pdf
- Questions: .txt, .pdf, .docx

**Check 2: File Size**
Max size: 10MB (Render free tier limit)

**Check 3: File Content**
- Students: Must have "Names" column
- Questions: Format "Question? Answer" (one per line)

---

## 📊 SYSTEM HEALTH INDICATORS

### Green (Healthy)
- ✅ Backend responds in < 2 seconds
- ✅ Frontend loads in < 3 seconds
- ✅ Login works immediately
- ✅ Quiz submission succeeds
- ✅ File uploads work
- ✅ Exports download successfully

### Yellow (Degraded)
- ⚠️ Backend responds in 30-60 seconds (cold start)
- ⚠️ Occasional timeouts
- ⚠️ Slow file uploads

### Red (Critical)
- ❌ Backend not responding
- ❌ Frontend 404
- ❌ Login always fails
- ❌ Database errors
- ❌ Data loss

---

## 🎯 FINAL VERIFICATION

### All Systems Go Checklist
- [ ] Backend health check passes
- [ ] Frontend loads correctly
- [ ] Admin can login
- [ ] Teacher can login
- [ ] Student can login
- [ ] Quiz creation works
- [ ] Quiz broadcast works
- [ ] Quiz submission works
- [ ] Results display correctly
- [ ] Exports work (PDF/Excel)
- [ ] Student upload works
- [ ] Teacher registration works
- [ ] Mobile interface works
- [ ] Data persists across sessions

### If ALL checked ✅
**🎉 SYSTEM IS FULLY OPERATIONAL!**

Your TVET Quiz System is ready for production use.

### If ANY unchecked ❌
**⚠️ ISSUES DETECTED**

Refer to troubleshooting section or contact support.

---

## 📱 QUICK ACCESS LINKS

**Production URLs:**
- Frontend: https://tsskqizi.pages.dev
- Backend: https://tvet-quiz-backend.onrender.com
- API Docs: https://tvet-quiz-backend.onrender.com/docs
- Health Check: https://tvet-quiz-backend.onrender.com/health

**Admin Dashboards:**
- Render: https://dashboard.render.com
- Cloudflare: https://dash.cloudflare.com
- GitHub: https://github.com/Leonardus437/Morning_Quiz

**Default Credentials:**
```
DOS Admin:
Username: admin
Password: admin123

Teacher:
Username: teacher001
Password: teacher123

Student:
Username: student001
Password: pass123
```

---

## 🆘 EMERGENCY CONTACTS

**If system is completely down:**
1. Check Render service status
2. Check Cloudflare deployment status
3. Check GitHub repository
4. Review recent commits
5. Rollback if needed

**Quick Fixes:**
- Backend down → Restart Render service
- Frontend down → Redeploy Cloudflare Pages
- Database issues → Check DATABASE_URL
- CORS errors → Verify backend CORS settings

---

**Last Updated**: 2025-01-XX
**System Version**: 1.8-SUBMISSION-FIX
**Deployment**: Production (Render + Cloudflare)
