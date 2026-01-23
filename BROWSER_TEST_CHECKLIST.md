# 🎯 BROWSER TEST CHECKLIST
**IMPORTANT:** Clear browser cache first! (Ctrl+Shift+Delete)

---

## ✅ TEST 1: Anti-Cheat Workflow (5 minutes)

### Setup:
1. Login as teacher: `teacher001` / `teacher123`
2. Create and broadcast a quiz
3. Logout

### Test:
1. Login as student: `student001` / `pass123`
2. Start the quiz
3. **Press ESC key** → Should see YELLOW modal "Warning #1"
4. Click "I Understand"
5. **Switch to another tab** → Should see YELLOW modal "Warning #2" IMMEDIATELY
6. Click "I Understand"
7. **Press F12 key** → Should see RED modal "Quiz Terminated"
8. **Verify:** "I Understand" button is HIDDEN
9. **Wait 3 seconds** → Quiz auto-submits
10. **Verify:** Redirected to results page with "Quiz Terminated" message

### Expected Result:
- ✅ 3 warnings triggered correctly
- ✅ RED modal on 3rd violation
- ✅ Button hidden when terminated
- ✅ Auto-submit after 3 seconds
- ✅ Results page shows termination message

---

## ✅ TEST 2: Teacher Notification (2 minutes)

### Test:
1. After completing Test 1, logout from student account
2. Login as teacher: `teacher001` / `teacher123`
3. Click **bell icon** in header
4. Look for notification: "⚠️ Cheating Alert: [Quiz Title]"
5. Read message - should include:
   - Student name: "Student One"
   - Violation count: "3 violations"
   - Reason: "You pressed a restricted key"

### Expected Result:
- ✅ Notification appears in bell icon dropdown
- ✅ Message includes student name and violation details

### If Not Working:
- Refresh the page (F5)
- Check browser console (F12) for errors
- Verify you're logged in as the teacher who created the quiz

---

## ✅ TEST 3: Score Calculation (3 minutes)

### Test:
1. Login as student: `student001` / `pass123`
2. Start a NEW quiz (not the terminated one)
3. **Open browser console** (F12)
4. Answer ALL questions
5. Click "Submit Quiz"
6. **Check console** - should see:
   ```
   📊 Submitting X/Y answers
   ✅ Quiz submitted successfully: {score: X, total: Y}
   ```
7. **Check results page** - score should display correctly (NOT "0/0 NaN%")

### Expected Result:
- ✅ Console shows correct answer count
- ✅ Results page shows correct score (e.g., "8/10 80%")

### If Showing "0/0 NaN%":
- Check console logs - what numbers appear?
- Take screenshot of console
- Report the exact numbers you see

---

## ✅ TEST 4: Tab Switch Warning Timing (1 minute)

### Test:
1. Start a quiz
2. **Try to switch tabs** (Ctrl+Tab or click another tab)
3. **Verify:** Warning appears IMMEDIATELY (before you leave)
4. Click "I Understand"
5. **Try to switch tabs again**
6. **Verify:** Warning appears again (no duplicate)

### Expected Result:
- ✅ Warning shows BEFORE leaving tab (not after returning)
- ✅ No duplicate warnings when modal is already open

---

## 🚨 TROUBLESHOOTING

### If Nothing Works:
1. **Clear browser cache:** Ctrl+Shift+Delete → Clear "Cached images and files"
2. **Hard refresh:** Ctrl+F5
3. **Try different browser:** Chrome, Firefox, Edge
4. **Check containers are running:**
   ```cmd
   docker ps
   ```

### If Specific Feature Doesn't Work:
1. Open browser console (F12)
2. Look for red error messages
3. Take screenshot
4. Report the exact error message

---

## 📊 QUICK REFERENCE

**Teacher Login:** `teacher001` / `teacher123`  
**Student Login:** `student001` / `pass123`  
**Frontend URL:** `http://localhost:3000`  
**Backend URL:** `http://localhost:8000`

**Restricted Keys That Trigger Warning:**
- ESC, F1-F12, Print Screen, Delete
- Home, End, Page Up, Page Down
- Windows keys

**Clear Cache Shortcut:** Ctrl+Shift+Delete  
**Hard Refresh Shortcut:** Ctrl+F5  
**Open Console Shortcut:** F12

---

**Total Test Time:** ~15 minutes  
**Status:** Ready to test in browser
