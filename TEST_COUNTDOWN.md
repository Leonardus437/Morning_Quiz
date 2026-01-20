# 🧪 Testing Countdown Timer Features

## 🚀 Quick Start Commands

### Option 1: Use the Restart Script
```cmd
cd C:\MorningQuiz
RESTART_SYSTEM.bat
```

### Option 2: Manual Commands
```cmd
cd C:\MorningQuiz
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

## 🧪 Test Scenarios

### 1. **Teacher Creates Quiz with Countdown**
1. Login as teacher: `SIBOMANA` / `12345678`
2. Go to "Create Quiz" tab
3. Set:
   - Title: "Countdown Test Quiz"
   - Duration: 5 minutes
   - **Time per Question: 30 seconds** ⏰
4. Select questions and create quiz
5. Click **"📡 Broadcast Now"** (this starts countdown immediately)

### 2. **Student Joins Quiz Immediately**
1. Login as student: `student001` / `student123`
2. Should see quiz with countdown timer
3. Click "🚀 Start Quiz"
4. Observe:
   - Total quiz timer (5 minutes)
   - Per-question timer (30 seconds)
   - Auto-submission when question time expires

### 3. **Student Joins Quiz Late**
1. Wait 2-3 minutes after broadcast
2. Login as different student
3. Should see "⚡ Time is going up, hurry up!" message
4. Remaining time should be accurate

### 4. **Test Auto-Submission**
1. Start quiz and don't answer a question
2. Wait for 30-second countdown to reach 0
3. Question should auto-submit
4. Should move to next question automatically
5. Cannot go back to expired question

### 5. **Test Quiz Expiration**
1. Wait for full quiz duration (5 minutes)
2. Try to access quiz
3. Should see "Quiz time is over!" message

## 🎯 Expected Behaviors

### ✅ **Teacher Interface**
- [x] "Time per Question" field in quiz creation
- [x] Shows per-question timing in quiz list
- [x] "Broadcast Now" starts countdown immediately
- [x] Enhanced notification messages

### ✅ **Student Dashboard**
- [x] Real-time countdown display
- [x] Color-coded warnings (yellow/red)
- [x] "Hurry Up!" messages for late joiners
- [x] "Quiz Time Over" for expired quizzes

### ✅ **Quiz Interface**
- [x] Dual timers (total + per-question)
- [x] Auto-submission when question time expires
- [x] Visual feedback for expired questions
- [x] Cannot return to completed questions
- [x] Color-coded question navigation

## 🔍 Visual Indicators to Look For

### **Timer Colors**
- 🟢 **Green**: Normal time remaining
- 🟡 **Yellow**: Warning (< 5 minutes total, < 10 seconds per question)
- 🔴 **Red**: Critical (< 1 minute total, < 5 seconds per question)
- ⚪ **Gray**: Expired/Disabled

### **Question Status**
- 🔵 **Blue**: Current question
- 🟢 **Green**: Answered question
- 🔴 **Red**: Auto-submitted (time expired)
- ⚪ **Gray**: Not attempted

### **Button States**
- **"📡 Broadcast Now"**: Starts countdown immediately
- **"⚡ Hurry Up!"**: Shows when time is running low
- **"⚠️ Quiz Time Over"**: Shows when quiz expired

## 🐛 Troubleshooting

### If countdown doesn't work:
1. Check browser console for errors
2. Verify server time synchronization
3. Clear browser cache and localStorage
4. Restart Docker containers

### If timers are incorrect:
1. Check system clock
2. Verify database timestamps
3. Clear quiz state in localStorage

## 📊 Test Data

### Sample Quiz Settings:
- **Duration**: 5 minutes (for quick testing)
- **Per Question**: 30 seconds
- **Questions**: 3-5 questions
- **Department**: Software Development
- **Level**: Level 3

### Test Accounts:
- **Teacher**: SIBOMANA / 12345678
- **Student 1**: student001 / student123
- **Student 2**: student002 / student123
- **Admin**: admin / admin123