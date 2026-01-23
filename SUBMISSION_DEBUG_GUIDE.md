# Quiz Submission Debugging Guide

## Issue
Students are unable to submit quizzes on production (`https://tsskwizi.pages.dev/`). The system shows "HTTP Error: Failed to fetch" when attempting to submit.

## Changes Made

### 1. Frontend API Logging (`frontend/src/lib/api.js`)
Added detailed logging to the `submitQuiz()` function:
- Logs submission data (quiz_id, answer count)
- Logs success/failure status
- Logs any errors that occur

### 2. Backend Submission Endpoint (`backend/main.py`)
Added comprehensive logging to `/quizzes/submit` endpoint:
- 📥 Logs incoming submission request with quiz_id, username, and answer count
- ✅ Logs quiz found confirmation
- ✅ Logs check for existing attempts
- ✅ Logs attempt creation with ID
- ✅ Logs grading completion with score and review status
- ✅ Logs database commit success/failure
- 📧 Logs teacher notification process
- ✅ Logs final submission completion

## How to Debug

### Step 1: Check Render Logs
1. Go to https://dashboard.render.com
2. Select your backend service
3. Click "Logs" tab
4. Look for these log messages when a student submits:

```
📥 SUBMIT REQUEST: quiz_id=X, user=studentXXX, answers_count=Y
✅ Quiz found: Quiz Title
✅ No existing attempt found, proceeding with submission
✅ Attempt created with ID: Z
✅ Grading complete: score=X/Y, needs_review=True/False
✅ Submission committed to database
📧 Notifying teacher Teacher Name (ID: X)
✅ Teacher notification sent
✅ SUBMISSION COMPLETE: attempt_id=Z, score=X
```

### Step 2: Check Browser Console
1. Open browser DevTools (F12)
2. Go to Console tab
3. Look for these messages:

```
📤 API: Submitting quiz with data: {quiz_id: X, answers_count: Y}
✅ API: Quiz submission successful: {score: X, total: Y, needs_review: true/false}
```

### Step 3: Identify the Problem

#### If you see "📥 SUBMIT REQUEST" in Render logs:
- Backend is receiving the request
- Check subsequent logs to see where it fails

#### If you DON'T see "📥 SUBMIT REQUEST" in Render logs:
- Request is not reaching the backend
- Possible causes:
  1. **CORS issue** - Check if browser console shows CORS error
  2. **Network timeout** - Render free tier may be sleeping (takes 60s to wake up)
  3. **Wrong backend URL** - Check `PUBLIC_API_URL` in frontend `.env.production`

#### If you see "❌" error logs:
- Read the error message to identify the specific issue
- Common errors:
  - "Quiz not found" - Quiz ID mismatch
  - "Quiz already submitted" - Student already completed this quiz
  - "Database commit failed" - Database connection issue

## Common Solutions

### Solution 1: Render Cold Start
**Problem**: Render free tier services sleep after 15 minutes of inactivity. First request takes 60+ seconds to wake up.

**Solution**: 
- Wait 60 seconds for the first submission
- Subsequent submissions will be fast
- Consider upgrading to paid tier for instant responses

### Solution 2: CORS Configuration
**Problem**: Browser blocks requests due to CORS policy.

**Solution**: Already configured in `backend/main.py`:
```python
allow_origins=[
    "https://tsskwizi.pages.dev",
    "https://d4e95bdd.tsskwizi.pages.dev",
    "http://localhost:3000",
    "http://localhost:5173",
    "*"
]
```

### Solution 3: Database Connection
**Problem**: PostgreSQL connection fails on Render.

**Solution**:
- Check Render dashboard for database status
- Verify `DATABASE_URL` environment variable is set correctly

### Solution 4: Quiz Already Submitted
**Problem**: Student tries to submit quiz twice.

**Solution**: Already handled in code:
- Frontend clears localStorage after successful submission
- Backend checks for existing attempts
- If attempt exists, returns 400 error

## Testing Checklist

1. ✅ Student can load quiz questions
2. ✅ Student can answer questions
3. ✅ Student can click "Submit" button
4. ✅ Submission shows loading state
5. ✅ Submission completes successfully
6. ✅ Student redirects to results page
7. ✅ Teacher receives notification
8. ✅ Submission appears in teacher review page

## Next Steps

1. **Deploy to Production**: Changes are already pushed to GitHub. Render will auto-deploy in 2-3 minutes.

2. **Test Submission**: Have a student attempt to submit a quiz and monitor:
   - Browser console for frontend logs
   - Render logs for backend logs

3. **Share Logs**: If issue persists, share:
   - Screenshot of browser console
   - Screenshot of Render logs
   - Exact error message shown to student

## Contact
If you need further assistance, provide:
1. Browser console screenshot
2. Render logs screenshot
3. Student username who experienced the issue
4. Quiz ID that failed to submit
5. Exact time of the failed submission attempt
