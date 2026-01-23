# 🔍 DEBUG: Finding the 602 Minutes Bug

## What I've Added

### 1. Debug Logging in Quiz Page
When a student starts a quiz, the browser console will now show:
```
🔍 DEBUG Quiz Data: {
  title: "Quiz Name",
  duration_minutes: 2,           ← Should be 2
  question_time_seconds: 30,     ← Should be 30
  calculated_seconds: 120        ← Should be 120 (2 × 60)
}

⏱️ Timer Calculation: {
  startTime: "...",
  now: "...",
  elapsedSeconds: 0,
  totalQuizTime: 120,            ← Should be 120
  timeLeft: 120                  ← Should be 120
}
```

### 2. Validation in Teacher Form
Now validates:
- Duration must be 1-180 minutes
- Question time must be 30-300 seconds
- Shows console log when creating quiz

### 3. Better Labels
- "⏱️ Total Quiz Duration (MINUTES)"
- "⏰ Time per Question (SECONDS)"
- Clear placeholders and help text

## How to Debug

### Step 1: Create a Test Quiz
1. Login as teacher
2. Create quiz with:
   - Total Duration: `2` minutes
   - Time per Question: `30` seconds
3. **Check browser console** - should see:
   ```
   📊 Creating quiz with timing: {
     duration_minutes: 2,
     question_time_seconds: 30,
     total_seconds: 120
   }
   ```

### Step 2: Start Quiz as Student
1. Login as student
2. Start the quiz
3. **Open browser console (F12)**
4. Look for the debug output
5. **Take a screenshot** of the console output

### Step 3: Check What's Wrong
If you see `duration_minutes: 602` in the console, then:
- ❌ The value 602 is being stored in the database
- ✅ The calculation is correct (602 × 60 = 36,120 seconds = 602 minutes)

If you see `duration_minutes: 2` but still see 602 minutes on screen:
- ✅ The database value is correct
- ❌ There's a display bug somewhere

## Possible Causes

### Cause 1: Old Quiz in Database
If you created a quiz BEFORE this fix, it might have the wrong value stored.
**Solution**: Delete old quizzes and create a new one.

### Cause 2: Browser Cache
Old JavaScript might be cached.
**Solution**: Hard refresh (Ctrl+Shift+R or Ctrl+F5)

### Cause 3: Field Swap
Maybe `duration_minutes` and `question_time_seconds` are swapped somewhere.
**Solution**: Check the console output to see which field has 602.

## Quick Test
1. Create quiz: Duration=`2`, Question Time=`30`
2. Expected result: Student sees "2:00" timer
3. If you see "602:00" or "10:02", check console logs
4. Share the console output with me

## Console Commands to Check Database
Open browser console and run:
```javascript
// Check what the API returns
fetch('/quizzes', {
  headers: { 'Authorization': 'Bearer ' + localStorage.getItem('token') }
})
.then(r => r.json())
.then(quizzes => {
  console.table(quizzes.map(q => ({
    id: q.id,
    title: q.title,
    duration_minutes: q.duration_minutes,
    question_time_seconds: q.question_time_seconds
  })));
});
```

This will show you EXACTLY what's stored in the database!
