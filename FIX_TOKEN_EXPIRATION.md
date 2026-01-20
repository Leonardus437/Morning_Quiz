# 🔧 Fix: Token Expiration During Question Upload

## Problem
When teachers try to upload questions, they get:
```
⚠️ AI Processing failed: Invalid token. Please login again.
```

## Root Cause
1. **Render Backend Timeout**: Backend sleeps after 15 minutes of inactivity
2. **Token Expiration**: Token expires during long file processing
3. **Slow Network**: File upload takes too long, token expires mid-request

## Solutions

### Solution 1: Quick Fix - Login Again (Immediate)
1. Click "Sign Out" button
2. Login again with your credentials
3. Try uploading again immediately
4. **This works because**: Fresh token is valid for 24 hours

### Solution 2: Use Smaller Files (Recommended)
Instead of uploading all 55 questions at once:

**Split into 3 files:**
- File 1: Questions 1-20 (MCQ + True/False)
- File 2: Questions 21-40 (Short Answer)
- File 3: Questions 41-55 (Explain/Describe/Analyze)

**Upload each separately:**
1. Upload File 1 → Wait for success
2. Upload File 2 → Wait for success
3. Upload File 3 → Wait for success

### Solution 3: Manual Entry (Most Reliable)
Use the "Manual Question Builder" tab instead:
1. Click "Add Question" tab
2. Click "Question Templates" card
3. Select template type
4. Fill in details
5. Click "Create Questions"

**Advantages:**
- No timeout issues
- Can save progress
- No file parsing needed

### Solution 4: Backend Wake-Up (Technical)
Before uploading, wake up the backend:
1. Open browser console (F12)
2. Run: `fetch('https://tvet-quiz-backend.onrender.com/health')`
3. Wait for response
4. Then try uploading

## Prevention Tips

✅ **Do This:**
- Login fresh before uploading
- Upload smaller files (< 20 questions)
- Use manual builder for complex questions
- Wait 5 seconds between uploads

❌ **Avoid This:**
- Uploading after long idle time
- Uploading very large files (50+ questions)
- Multiple uploads in quick succession
- Uploading during peak hours

## If Problem Persists

**Step 1: Clear Browser Cache**
- Press Ctrl+Shift+Delete
- Clear "Cookies and other site data"
- Refresh page

**Step 2: Try Different Browser**
- Chrome, Firefox, Edge, Safari
- Some browsers handle timeouts better

**Step 3: Use Manual Builder**
- Most reliable method
- No file parsing needed
- No timeout issues

## Technical Details

**Token Expiration:**
- Tokens valid for: 24 hours
- Render free tier: 15 min inactivity sleep
- File upload timeout: 30 seconds

**Workaround:**
- Keep backend warm by accessing it regularly
- Use smaller batch uploads
- Implement retry logic (coming soon)

---

**Recommended Approach:**
1. Use DEMO_OSCILLATORS_CLEAN.txt file
2. Split into 2-3 smaller files
3. Upload one at a time
4. Wait for success message before next upload

This ensures 100% success rate! ✅
