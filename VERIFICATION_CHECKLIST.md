# 🧪 Morning Quiz System - Verification Checklist

## ✅ Core Features to Test

### 1. **Authentication**
- [ ] Admin login works (`admin` / `admin123`)
- [ ] Teacher login works (`teacher001` / `teacher123`)
- [ ] Student login works (`student001` / `pass123`)

### 2. **Quiz Management (Teacher)**
- [ ] Teacher can create quizzes
- [ ] Teacher can add questions to quiz
- [ ] Teacher can see their quizzes in dashboard

### 3. **Quiz Broadcast (CRITICAL)**
- [ ] Teacher clicks "Activate/Broadcast" button
- [ ] Button shows "✅ Live & Broadcasting" status
- [ ] System shows number of students notified
- [ ] Quiz `is_active` flag is set to `true` in database

### 4. **Student Quiz Visibility (CRITICAL)**
- [ ] Student logs in
- [ ] Student dashboard shows active quizzes
- [ ] Quiz appears in student's available quizzes list
- [ ] Quiz title and description are visible
- [ ] "Start Quiz" button is available

### 5. **Quiz Access**
- [ ] Student can click "Start Quiz"
- [ ] Quiz questions load properly
- [ ] Student can answer questions
- [ ] Student can submit answers

### 6. **Notifications**
- [ ] Student receives notification when quiz is broadcast
- [ ] Notification shows quiz title and instructions
- [ ] Notification appears in student's notification panel

### 7. **Results & Leaderboard**
- [ ] Teacher can view quiz results
- [ ] Leaderboard shows student scores
- [ ] Results can be exported to Excel/PDF

### 8. **Real-time Updates**
- [ ] When teacher broadcasts, students see it immediately
- [ ] No page refresh needed for students to see quiz
- [ ] Countdown timer works correctly

---

## 🚀 Quick Test Steps

### Step 1: Start System
```bash
docker-compose up -d
```

### Step 2: Run Test Script
```bash
python test_complete_system.py
```

### Step 3: Manual Testing
1. Open `http://localhost:3000/teacher` → Login as teacher
2. Create a quiz with questions
3. Click "Activate/Broadcast"
4. Open new browser/incognito → `http://localhost:3000` → Login as student
5. Verify quiz appears in student dashboard
6. Click "Start Quiz" and answer questions
7. Submit and check results

---

## 🔍 Debugging Tips

### If Quiz Not Showing to Student:
1. Check database: `SELECT * FROM quizzes WHERE is_active = 1;`
2. Verify student department/level matches quiz
3. Check browser console for errors
4. Clear browser cache and refresh

### If Broadcast Button Not Working:
1. Check backend logs: `docker logs morning_quiz_backend`
2. Verify teacher is logged in
3. Ensure quiz has questions
4. Check network tab in browser DevTools

### If Notifications Not Appearing:
1. Check notifications table in database
2. Verify student ID is correct
3. Refresh notifications panel

---

## 📊 Expected Behavior

| Action | Expected Result |
|--------|-----------------|
| Teacher broadcasts quiz | ✅ Status shows "Live & Broadcasting" |
| Student logs in | ✅ Active quiz appears in dashboard |
| Student clicks quiz | ✅ Questions load without errors |
| Student submits answers | ✅ Score calculated and saved |
| Teacher views results | ✅ Leaderboard shows all submissions |

---

## ✨ Success Criteria

- ✅ All 8 features working
- ✅ No console errors
- ✅ Quiz reaches students within 1 second of broadcast
- ✅ All data persists correctly
- ✅ System handles 50+ concurrent users

---

**Last Updated:** $(date)
**Status:** Ready for Testing
