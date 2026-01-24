# Quick Test Guide - Chat System

## ✅ Test Checklist

### 1. Visual Check
- [ ] Start the system: `docker-compose up -d`
- [ ] Open browser: `http://localhost:3000`
- [ ] Login as student (student001 / pass123)
- [ ] **VERIFY**: Chat button appears in bottom-LEFT corner
- [ ] **VERIFY**: Button has gradient blue-purple color
- [ ] **VERIFY**: Hover shows "Knowledge Hub 💬" tooltip

### 2. Admin - Class Teacher Assignment
- [ ] Login as admin (admin / admin123)
- [ ] Go to Admin Dashboard
- [ ] Click "🎓 Class Teachers" tab
- [ ] Select teacher: "Teacher One"
- [ ] Select department: "Software Development"
- [ ] Select level: "Level 5"
- [ ] Click "Assign Class Teacher"
- [ ] **VERIFY**: Success message appears
- [ ] **VERIFY**: Assignment shows in table below

### 3. Admin - Create Class Chat Room
- [ ] Click chat button (bottom-left)
- [ ] Click "+ New Room"
- [ ] Enter name: "L5 Software Development Class"
- [ ] Select type: "Students & Teachers"
- [ ] Select department: "Software Development"
- [ ] Select level: "Level 5"
- [ ] Click "Create"
- [ ] **VERIFY**: Success popup shows participant count
- [ ] **VERIFY**: Room appears in list

### 4. Teacher - View Chat Room
- [ ] Logout from admin
- [ ] Login as teacher (teacher001 / teacher123)
- [ ] Click chat button (bottom-left)
- [ ] **VERIFY**: See "L5 Software Development Class" room
- [ ] Click on the room
- [ ] Type message: "Hello students!"
- [ ] Click "Send 📤"
- [ ] **VERIFY**: Message appears

### 5. Student - Join and Chat
- [ ] Logout from teacher
- [ ] Login as student (student001 / pass123)
- [ ] Click chat button (bottom-left)
- [ ] **VERIFY**: See "L5 Software Development Class" room
- [ ] Click on the room
- [ ] **VERIFY**: See teacher's message
- [ ] Type reply: "Hello teacher!"
- [ ] Click "Send 📤"
- [ ] **VERIFY**: Message appears

### 6. Real-Time Test
- [ ] Open two browser windows side-by-side
- [ ] Window 1: Login as teacher
- [ ] Window 2: Login as student
- [ ] Both: Open same chat room
- [ ] Teacher: Send message
- [ ] **VERIFY**: Student sees message within 2 seconds
- [ ] Student: Send reply
- [ ] **VERIFY**: Teacher sees reply within 2 seconds

### 7. Student Group Chat
- [ ] Login as student
- [ ] Click chat button
- [ ] Click "+ New Room"
- [ ] Name: "Study Group - Blockchain"
- [ ] Type: "Students Only"
- [ ] Department: "Software Development"
- [ ] Level: "Level 5"
- [ ] Click "Create"
- [ ] **VERIFY**: Room created
- [ ] **VERIFY**: Other students from same class can see it

## 🎯 Expected Results

### Chat Button:
- ✅ Appears in bottom-LEFT corner (not right)
- ✅ Gradient blue-purple color
- ✅ Smooth hover animation
- ✅ Shows on all pages when logged in
- ✅ Tooltip on hover

### Class Teacher Assignment:
- ✅ Admin can assign teachers to classes
- ✅ Shows in table with teacher name, dept, level
- ✅ Can remove assignments
- ✅ Teacher gets notification

### Chat Room Creation:
- ✅ Admin/Teacher can create rooms
- ✅ Students automatically added based on dept/level
- ✅ Class teacher automatically added
- ✅ All participants get notifications
- ✅ Participant count shown

### Real-Time Messaging:
- ✅ Messages appear within 2 seconds
- ✅ Sender name and role shown
- ✅ Timestamp on each message
- ✅ Auto-scroll to latest message
- ✅ Different colors for different roles

## 🐛 Common Issues & Fixes

### Issue: Chat button not showing
**Fix**: 
- Clear browser cache (Ctrl+Shift+Delete)
- Hard refresh (Ctrl+F5)
- Check you're logged in
- Verify FloatingChatButton is in layout

### Issue: Can't create chat room
**Fix**:
- Ensure department and level are selected
- Check you have permission for room type
- Verify backend is running: `docker-compose ps`

### Issue: Messages not updating
**Fix**:
- Check internet connection
- Verify backend is running
- Check browser console for errors
- Try refreshing the page

### Issue: Class teacher not added to room
**Fix**:
- Verify class teacher is assigned first
- Check department and level match exactly
- Recreate the room after assignment

## 📊 Database Verification

### Check class teacher assignments:
```sql
SELECT ct.*, u.full_name as teacher_name 
FROM class_teachers ct 
JOIN users u ON ct.teacher_id = u.id;
```

### Check chat rooms:
```sql
SELECT * FROM chat_rooms;
```

### Check chat participants:
```sql
SELECT cr.name, u.full_name, u.role 
FROM chat_participants cp
JOIN chat_rooms cr ON cp.room_id = cr.id
JOIN users u ON cp.user_id = u.id
ORDER BY cr.name, u.role;
```

### Check messages:
```sql
SELECT cr.name as room, u.full_name as sender, cm.message, cm.created_at
FROM chat_messages cm
JOIN chat_rooms cr ON cm.room_id = cr.id
JOIN users u ON cm.sender_id = u.id
ORDER BY cm.created_at DESC
LIMIT 20;
```

## 🎉 Success Criteria

All tests pass when:
- ✅ Chat button visible in bottom-LEFT
- ✅ Admin can assign class teachers
- ✅ Chat rooms auto-add participants
- ✅ Messages appear in real-time
- ✅ All user roles can access appropriate rooms
- ✅ Notifications work
- ✅ No console errors

## 📝 Test Report Template

```
Date: ___________
Tester: ___________

Visual Check: ☐ Pass ☐ Fail
Class Teacher Assignment: ☐ Pass ☐ Fail
Chat Room Creation: ☐ Pass ☐ Fail
Teacher Chat: ☐ Pass ☐ Fail
Student Chat: ☐ Pass ☐ Fail
Real-Time Updates: ☐ Pass ☐ Fail
Student Groups: ☐ Pass ☐ Fail

Issues Found:
_________________________________
_________________________________
_________________________________

Overall Status: ☐ All Working ☐ Needs Fixes

Notes:
_________________________________
_________________________________
```

## 🚀 Next Steps After Testing

1. ✅ All tests pass → System ready for production
2. ⚠️ Some tests fail → Check troubleshooting section
3. 🐛 Major issues → Review implementation guide
4. 📚 Need help → Check CHAT_AND_CLASS_TEACHER_GUIDE.md

## 💡 Pro Tips

- Test with multiple users simultaneously
- Try different departments and levels
- Test on mobile devices
- Check with slow internet connection
- Verify notifications work
- Test message deletion
- Try flagging messages (as DOS)

---

**Happy Testing! 🎉**
