# 🚀 Quick Start - Test Everything

## Step 1: Restart System
```bash
cd C:\TVETQuiz
docker-compose down
docker-compose up -d
```

Wait 30 seconds for services to start.

## Step 2: Test in Browser

### Teacher Dashboard
1. Open: `http://localhost:3000/teacher`
2. Login: `teacher001` / `teacher123`
3. Create a quiz (if none exists)
4. Click **"Activate/Broadcast"** button
5. Verify it shows: **✅ Live & Broadcasting**

### Student Dashboard (New Tab/Incognito)
1. Open: `http://localhost:3000`
2. Login: `student001` / `pass123`
3. **Verify quiz appears** in the dashboard
4. Click **"Start Quiz"**
5. Answer questions and submit

## Step 3: Verify Key Points

✅ **Quiz Broadcast:**
- Teacher sees "Live & Broadcasting" status
- Shows number of students notified

✅ **Student Visibility:**
- Quiz appears immediately after broadcast
- No page refresh needed
- Quiz title and description visible

✅ **Quiz Access:**
- Student can click and start quiz
- Questions load properly
- Can submit answers

✅ **Results:**
- Score calculated correctly
- Appears in leaderboard
- Teacher can view results

## Step 4: Run Automated Test
```bash
python test_complete_system.py
```

Expected output:
```
✅ Admin Login: PASS
✅ Teacher Login: PASS
✅ Student Login: PASS
✅ Quiz Broadcast: PASS
✅ Student Sees Quiz: PASS
✅ Notifications: PASS

🎉 ALL TESTS PASSED - SYSTEM WORKING PERFECTLY!
```

## Troubleshooting

**Quiz not showing to student?**
- Check student department/level matches quiz
- Verify quiz is_active = 1 in database
- Clear browser cache

**Broadcast button not working?**
- Check backend logs: `docker logs morning_quiz_backend`
- Ensure quiz has questions
- Verify teacher is logged in

**Need to reset?**
```bash
docker-compose down -v
docker-compose up -d
```

---

**All features working? You're ready to go! 🎉**
