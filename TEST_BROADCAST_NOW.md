# Test Quiz Broadcast - Step by Step

## Prerequisites
- System is running: `docker-compose up -d`
- Backend is healthy: `curl http://localhost:8000/health`
- You have teacher and student accounts

## Test Scenario

### Step 1: Verify Student Setup (5 minutes)

**Go to DOS Admin Panel:**
1. Open http://localhost:3000/admin
2. Login as DOS: `admin` / `admin123`
3. Go to **Student Management**
4. Check students exist with:
   - Department: `Computer System and Architecture`
   - Level: `Level 3`

**If no students:**
1. Click **Upload Students**
2. Upload a file or add manually
3. Make sure to set Department and Level

**Example student:**
```
Username: student001
Full Name: Test Student
Department: Computer System and Architecture
Level: Level 3
```

### Step 2: Create Quiz (5 minutes)

**Go to Teacher Panel:**
1. Open http://localhost:3000/teacher
2. Login as teacher: `teacher001` / `teacher123`
3. Go to **Create Quiz** tab

**Create quiz:**
1. Title: `Test Broadcast Quiz`
2. Description: `Testing quiz broadcast functionality`
3. Department: `Computer System and Architecture` (MUST MATCH STUDENT)
4. Level: `Level 3` (MUST MATCH STUDENT)
5. Scheduled Time: Pick any future time
6. Duration: `30` minutes
7. Time per question: `60` seconds

**Add questions:**
1. Click **Add Question** or use **AI Document Parser**
2. Add at least 1 question
3. Make sure to set:
   - Department: `Computer System and Architecture`
   - Level: `Level 3`
   - Lesson: Select any lesson

**Create quiz:**
1. Click **Create Quiz**
2. Should see: `✅ Quiz created successfully!`

### Step 3: Broadcast Quiz (2 minutes)

**Go to My Quizzes:**
1. Click **🎮 My Quizzes** tab
2. Find your quiz (should show ⚪ Draft status)

**Broadcast:**
1. Click **📡 Broadcast Now** button
2. **IMPORTANT**: Check the alert message
3. Should see: `Quiz broadcasted to all students immediately! Students notified: X`
4. **X should be > 0** (if X = 0, there's a mismatch)

**Check backend logs:**
```bash
docker-compose logs backend --tail=20
```

Should see:
```
🎯 BROADCASTING QUIZ X
   Quiz: Test Broadcast Quiz
   Department: Computer System and Architecture
   Level: Level 3
   Found 1 students to notify
   - Notifying: student001 (Computer System and Architecture - Level 3)
   ✅ Quiz X is now ACTIVE and BROADCASTING
```

### Step 4: Verify Student Sees Quiz (3 minutes)

**Go to Student Portal:**
1. Open http://localhost:3000 (or http://localhost:3000/student)
2. Login as student: `student001` / `pass123`
3. You should see the quiz in **AVAILABLE QUIZZES**

**If quiz doesn't appear:**
1. Refresh page (Ctrl+F5)
2. Wait 2-3 seconds
3. Check backend logs for errors

**Check backend logs:**
```bash
docker-compose logs backend --tail=20
```

Should see:
```
🔍 STUDENT QUIZ FETCH: student001
   Student Dept/Level: Computer System and Architecture - Level 3
   📊 Total ACTIVE quizzes in system: 1
      Quiz X: 'Test Broadcast Quiz' | Dept: Computer System and Architecture | Level: Level 3
   ✅ Filtered quizzes for student001: 1 matches
      ✓ Quiz X: 'Test Broadcast Quiz'
```

### Step 5: Take Quiz (5 minutes)

**Student takes quiz:**
1. Click on the quiz
2. Should see questions
3. Should see timer counting down
4. Answer questions
5. Click **Submit**
6. Should see results

**Teacher checks results:**
1. Go back to teacher panel
2. Go to **My Quizzes**
3. Click **📈 View Results**
4. Should see student's submission

## Troubleshooting

### Problem: "Students notified: 0"

**Check 1: Student Department/Level**
```bash
curl http://localhost:8000/debug/students
```
Look for your student and verify:
- `"department": "Computer System and Architecture"`
- `"level": "Level 3"`

**Check 2: Quiz Department/Level**
```bash
curl http://localhost:8000/debug/quizzes
```
Look for your quiz and verify:
- `"department": "Computer System and Architecture"`
- `"level": "Level 3"`

**Check 3: Exact Match**
- Student dept must EXACTLY match quiz dept
- Student level must EXACTLY match quiz level
- No extra spaces or different capitalization

**Fix:**
1. Delete quiz
2. Delete student
3. Recreate both with EXACT same dept/level
4. Try broadcast again

### Problem: Quiz appears but student can't access

**Check 1: Quiz is active**
```bash
curl http://localhost:8000/debug/quizzes
```
Look for your quiz:
- `"is_active": true`
- `"countdown_started_at"` should be set

**Check 2: Quiz time hasn't expired**
- Check `countdown_started_at` timestamp
- Calculate: current_time - countdown_started_at < duration_minutes * 60
- If expired, create new quiz

**Check 3: Student has questions**
- Quiz must have at least 1 question
- Questions must have correct answers

### Problem: Backend logs show errors

**Check logs:**
```bash
docker-compose logs backend --tail=100
```

**Common errors:**
- `Department mismatch` - Quiz dept != Student dept
- `Level mismatch` - Quiz level != Student level
- `No questions` - Quiz has no questions
- `Student not found` - Student doesn't exist

**Fix:**
1. Read error message carefully
2. Fix the issue (create student, add questions, etc.)
3. Try again

## Success Checklist

- [ ] Student created with dept/level
- [ ] Quiz created with SAME dept/level
- [ ] Quiz has at least 1 question
- [ ] Teacher broadcasts quiz
- [ ] Alert shows "Students notified: X" (X > 0)
- [ ] Backend logs show broadcast confirmation
- [ ] Student sees quiz in AVAILABLE QUIZZES
- [ ] Student can click and open quiz
- [ ] Student can see questions
- [ ] Student can submit answers
- [ ] Teacher can see results

## Quick Commands

**Check system health:**
```bash
curl http://localhost:8000/health
```

**See all quizzes:**
```bash
curl http://localhost:8000/debug/quizzes
```

**See all students:**
```bash
curl http://localhost:8000/debug/students
```

**Check backend logs:**
```bash
docker-compose logs backend --tail=50
```

**Restart backend:**
```bash
docker-compose restart backend
```

**Full restart:**
```bash
docker-compose down
docker-compose up -d
```

## Expected Timeline

- Setup: 5 minutes
- Create quiz: 5 minutes
- Broadcast: 2 minutes
- Verify: 3 minutes
- Take quiz: 5 minutes
- **Total: ~20 minutes**

## Support

If something doesn't work:
1. Check all troubleshooting steps above
2. Verify backend logs
3. Verify student/quiz dept/level match
4. Try full restart
5. Report with:
   - Quiz ID and title
   - Student username
   - Department/Level values
   - Backend logs (last 100 lines)
