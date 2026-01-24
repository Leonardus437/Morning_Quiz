# Testing Guide - Class Teacher & Chat System

## Prerequisites
1. Backend running: `cd backend && uvicorn main:app --reload`
2. Frontend running: `cd frontend && npm run dev`
3. Login as admin: `admin` / `admin123`

## Test Scenarios

### 1. Assign Class Teacher
**Steps:**
1. Login as admin
2. Go to "Class Teachers" tab
3. Select a teacher from dropdown
4. Select department (e.g., "Software Development")
5. Select level (e.g., "Level 5")
6. Click "Assign Class Teacher"

**Expected:**
- Success message appears
- Assignment shows in table below
- Teacher is now class teacher for that dept+level

### 2. Class Teacher Creates Student-Teacher Room
**Steps:**
1. Logout, login as the class teacher you just assigned
2. Click chat button (bottom right)
3. Click "Create New Chat"
4. Select room type: "Student-Teacher (Academic Support)"
5. Select THEIR assigned department and level
6. Enter room name
7. Click "Create Room"

**Expected:**
- Room created successfully
- All students from that dept/level added
- ONLY that class teacher added (not other teachers)
- Notifications sent to all participants

### 3. Class Teacher Tries to Create Room for Other Class
**Steps:**
1. As class teacher, try to create student-teacher room
2. Select DIFFERENT department or level (not their assigned one)
3. Try to create

**Expected:**
- Error: "Can only create rooms for your assigned class"
- Room NOT created

### 4. Module Teacher Creates Module Room
**Steps:**
1. Login as teacher (NOT class teacher)
2. Admin must first assign them to a module:
   - Admin → Assignments tab
   - Select teacher
   - Assign a lesson/module
3. Teacher opens chat
4. Can ONLY select "Module/Lesson Group" room type
5. Select their assigned module
6. Create room

**Expected:**
- Room created
- Students from module's dept/level added
- ONLY teachers assigned to that module added
- Notifications sent

### 5. Module Teacher Tries to Create Student-Teacher Room
**Steps:**
1. As module teacher (not class teacher)
2. Try to select "Student-Teacher" room type
3. Try to create

**Expected:**
- Error: "You can only create module-based rooms"
- Room NOT created

### 6. Admin Creates Any Room
**Steps:**
1. Login as admin
2. Open chat
3. Can create ANY room type
4. No restrictions

**Expected:**
- All room types available
- Can create for any dept/level
- No permission errors

### 7. View Notifications
**Steps:**
1. As student, check notifications
2. Should see "Added to Chat Room" notification
3. Click chat button
4. Room should appear in sidebar

**Expected:**
- Notification received
- Room visible
- Can send messages

## Quick Test Commands

```bash
# Start backend
cd backend
uvicorn main:app --reload

# Start frontend (new terminal)
cd frontend
npm run dev

# Access
# Admin: http://localhost:5173/admin
# Teacher: http://localhost:5173/teacher
# Student: http://localhost:5173
```

## Test Accounts

**Admin:**
- Username: `admin`
- Password: `admin123`

**Teacher:**
- Username: `teacher001`
- Password: `teacher123`

**Student:**
- Username: `student001`
- Password: `pass123`

## Verification Checklist

- [ ] Class teacher can be assigned
- [ ] Class teacher can create rooms for their class
- [ ] Class teacher CANNOT create rooms for other classes
- [ ] Module teacher can ONLY create module rooms
- [ ] Module teacher CANNOT create student-teacher rooms
- [ ] Student-teacher rooms add ONLY class teacher
- [ ] Module rooms add ONLY assigned teachers
- [ ] Notifications sent to all participants
- [ ] Chat modal shows module dropdown
- [ ] Admin can create any room type
- [ ] Students can see and join rooms
- [ ] Messages send/receive correctly

## Common Issues

**"Token required" error:**
- Logout and login again
- Check browser console for token

**"Room not created":**
- Check backend console for error details
- Verify teacher has proper assignments

**"No participants added":**
- Check if students exist for that dept/level
- Check if class teacher is assigned
- Check if teachers are assigned to module

**Chat button not showing:**
- Check if user is logged in
- Check localStorage for user object
- Refresh page

## Database Check

```python
# Check class teacher assignments
SELECT * FROM class_teachers;

# Check chat rooms
SELECT * FROM chat_rooms;

# Check participants
SELECT * FROM chat_participants;

# Check notifications
SELECT * FROM notifications ORDER BY created_at DESC LIMIT 10;
```
