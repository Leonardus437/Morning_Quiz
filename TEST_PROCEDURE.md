# 🧪 EXACT TEST PROCEDURE

## Step 1: Start the System
```bash
cd C:\TVETQuiz
docker-compose up -d
```

## Step 2: Login as Teacher KANGABO

1. Open browser: `http://localhost:3000/teacher`
2. Login:
   - Username: `KANGABO`
   - Password: `12345678`
3. **Open Browser Console (F12)** - Keep it open!

## Step 3: Create a Test Quiz

1. Click "Create Quiz" tab
2. Fill in:
   - **Title**: `Test Quiz 602 Debug`
   - **Description**: `Testing timing issue`
   - **Department**: Select any (e.g., "Software Development")
   - **Level**: Select any (e.g., "Level 3")
   - **Scheduled Time**: Select current time
   - **⏱️ Total Quiz Duration (MINUTES)**: Enter `2`
   - **⏰ Time per Question (SECONDS)**: Enter `30`
3. Select at least 1 question
4. Click "Create Quiz"
5. **CHECK CONSOLE** - You should see:
   ```
   📊 Creating quiz with timing: {
     duration_minutes: 2,
     question_time_seconds: 30,
     total_seconds: 120
   }
   ```
   **📸 TAKE SCREENSHOT OF THIS!**

## Step 4: Broadcast the Quiz

1. Go to "My Quizzes" tab
2. Find your quiz "Test Quiz 602 Debug"
3. Click "Activate" button
4. Click "Broadcast Now" button
5. Wait for confirmation

## Step 5: Login as Student

1. Open NEW browser tab (or incognito window): `http://localhost:3000`
2. Click "Student Login"
3. Login:
   - Username: `MASENGESHO Yves Smyrne` (or just the username part)
   - Password: `student123`
4. **Keep Console Open (F12)**

## Step 6: Start the Quiz

1. You should see "Test Quiz 602 Debug" in the list
2. Click "Start Quiz"
3. **IMMEDIATELY CHECK CONSOLE** - You should see:
   ```
   🔍 DEBUG Quiz Data: {
     title: "Test Quiz 602 Debug",
     duration_minutes: ???,           ← WHAT NUMBER IS HERE?
     question_time_seconds: ???,      ← WHAT NUMBER IS HERE?
     calculated_seconds: ???          ← WHAT NUMBER IS HERE?
   }
   
   ⏱️ Timer Calculation: {
     startTime: "...",
     now: "...",
     elapsedSeconds: ???,
     totalQuizTime: ???,              ← WHAT NUMBER IS HERE?
     timeLeft: ???                    ← WHAT NUMBER IS HERE?
   }
   ```
4. **📸 TAKE SCREENSHOT OF CONSOLE OUTPUT!**
5. **📸 TAKE SCREENSHOT OF THE TIMER ON SCREEN!**

## Step 7: Check What You See

### On Screen:
- What does the timer show? (e.g., "2:00" or "602:00" or "10:02"?)

### In Console:
- What is `duration_minutes`? (Should be 2)
- What is `question_time_seconds`? (Should be 30)
- What is `calculated_seconds`? (Should be 120)
- What is `totalQuizTime`? (Should be 120)
- What is `timeLeft`? (Should be 120 or less)

## Expected Results

✅ **CORRECT:**
- Console shows: `duration_minutes: 2`
- Console shows: `calculated_seconds: 120`
- Screen shows: `2:00` timer

❌ **BUG FOUND:**
- Console shows: `duration_minutes: 602` → Database has wrong value
- Console shows: `duration_minutes: 2` but screen shows `602:00` → Display bug
- Console shows: `calculated_seconds: 36120` → Wrong calculation

## Alternative: Check Database Directly

In browser console (F12), run this:
```javascript
fetch('http://localhost:8000/quizzes', {
  headers: { 
    'Authorization': 'Bearer ' + localStorage.getItem('token'),
    'Content-Type': 'application/json'
  }
})
.then(r => r.json())
.then(quizzes => {
  const testQuiz = quizzes.find(q => q.title.includes('Test Quiz 602'));
  console.log('📊 DATABASE VALUES:', {
    title: testQuiz.title,
    duration_minutes: testQuiz.duration_minutes,
    question_time_seconds: testQuiz.question_time_seconds,
    calculated: testQuiz.duration_minutes * 60
  });
});
```

This will show EXACTLY what's in the database!

## What to Share

Please share:
1. Screenshot of teacher console when creating quiz
2. Screenshot of student console when starting quiz
3. Screenshot of the timer on student screen
4. The numbers you see in the console logs

This will tell us EXACTLY where 602 is coming from! 🎯
