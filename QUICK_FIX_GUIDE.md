# Quick Fix Guide - Quiz Not Reaching Students

## The Problem
Teacher clicks "Activate/Broadcast" but students don't see the quiz.

## The Solution
The issue is **department/level mismatch**. Follow these steps:

### Step 1: Verify Student Setup
1. Go to **DOS Admin Panel** → **Student Management**
2. Check that students have:
   - ✅ Correct **Department** assigned
   - ✅ Correct **Level** assigned
   - ✅ Active status

Example:
```
Student: AGASARO NSENGIYUMVA Audrey
Department: Computer System and Architecture
Level: Level 3
```

### Step 2: Create Quiz with Matching Department/Level
1. Go to **Teacher Panel** → **Create Quiz**
2. Select the **SAME** department/level as your students:
   - Department: `Computer System and Architecture`
   - Level: `Level 3`
3. Add questions
4. Click **Create Quiz**

### Step 3: Broadcast the Quiz
1. Go to **My Quizzes** tab
2. Find your quiz (should show ⚪ Draft status)
3. Click **📡 Broadcast Now** button
4. You should see: `Quiz broadcasted to all students immediately! Students notified: X`

### Step 4: Verify on Student Side
1. Open **Student Portal** (http://localhost:3000)
2. Login as a student from that department/level
3. You should see the quiz in **AVAILABLE QUIZZES**
4. Quiz should show with timer running

## Common Issues & Fixes

### Issue 1: "Students notified: 0"
**Problem**: No students matched the quiz department/level

**Fix**:
1. Check quiz department/level
2. Check student department/level
3. Make sure they EXACTLY match
4. Recreate quiz if needed

### Issue 2: Quiz appears but says "NO ACTIVE QUIZZES"
**Problem**: Quiz wasn't properly broadcasted

**Fix**:
1. Go back to teacher panel
2. Click **📡 Broadcast Now** again
3. Check the notification count
4. Refresh student page

### Issue 3: Student can't access quiz
**Problem**: Quiz time expired or access denied

**Fix**:
1. Check quiz duration (should be > 0 minutes)
2. Check if quiz time has elapsed
3. Verify student department/level matches quiz

## Quick Checklist

Before broadcasting:
- [ ] Students created with department/level
- [ ] Quiz created with SAME department/level
- [ ] Quiz has questions added
- [ ] Quiz duration set (e.g., 30 minutes)

After broadcasting:
- [ ] Teacher sees "Students notified: X" (X > 0)
- [ ] Student page shows quiz in AVAILABLE QUIZZES
- [ ] Quiz timer is counting down
- [ ] Student can click and start quiz

## Debug Commands

Check all quizzes:
```bash
curl http://localhost:8000/debug/quizzes
```

Check all students:
```bash
curl http://localhost:8000/debug/students
```

Check backend logs:
```bash
docker-compose logs backend --tail=50
```

## Still Not Working?

1. **Restart everything**:
   ```bash
   docker-compose down
   docker-compose up -d
   ```

2. **Check logs for errors**:
   ```bash
   docker-compose logs backend
   ```

3. **Verify database**:
   - Check quiz is marked `is_active = true`
   - Check quiz has `countdown_started_at` set
   - Check student has department/level assigned

4. **Contact support** with:
   - Quiz ID and title
   - Student username
   - Department/Level values
   - Backend logs (last 50 lines)
