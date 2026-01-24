# Backend Update Required for Chat Notifications

## Current Status
✅ Room creation is working
❌ Notifications are NOT being sent to students when added to rooms

## Required Changes in main.py

Find the `create_chat_room` function (around line 2196) and make these changes:

### 1. Add notify_participants parameter
After line:
```python
level = data.get("level")
```

Add:
```python
notify_participants = data.get("notify_participants", True)
```

### 2. Track participants being added
After line:
```python
db.add(participant)
```

Add:
```python
participants_added = []
```

### 3. Update each participant addition loop

**For student-student rooms:**
Change:
```python
for student in students:
    if student.id != current_user.id:
        p = ChatParticipant(room_id=room.id, user_id=student.id)
        db.add(p)
```

To:
```python
for student in students:
    if student.id != current_user.id:
        p = ChatParticipant(room_id=room.id, user_id=student.id)
        db.add(p)
        participants_added.append(student)
```

**For student-teacher rooms (students):**
Change:
```python
for student in students:
    p = ChatParticipant(room_id=room.id, user_id=student.id)
    db.add(p)
```

To:
```python
for student in students:
    p = ChatParticipant(room_id=room.id, user_id=student.id)
    db.add(p)
    participants_added.append(student)
```

**For student-teacher rooms (teachers):**
Change:
```python
for teacher in teachers:
    if teacher.departments and department in teacher.departments:
        p = ChatParticipant(room_id=room.id, user_id=teacher.id)
        db.add(p)
```

To:
```python
for teacher in teachers:
    if teacher.departments and department in teacher.departments:
        p = ChatParticipant(room_id=room.id, user_id=teacher.id)
        db.add(p)
        participants_added.append(teacher)
```

**For teacher-teacher rooms:**
Change:
```python
for teacher in teachers:
    if teacher.id != current_user.id:
        p = ChatParticipant(room_id=room.id, user_id=teacher.id)
        db.add(p)
```

To:
```python
for teacher in teachers:
    if teacher.id != current_user.id:
        p = ChatParticipant(room_id=room.id, user_id=teacher.id)
        db.add(p)
        participants_added.append(teacher)
```

**For teacher-dos rooms:**
Change:
```python
for teacher in teachers:
    p = ChatParticipant(room_id=room.id, user_id=teacher.id)
    db.add(p)
# Add DOS
admins = db.query(User).filter(User.role == "admin").all()
for admin in admins:
    p = ChatParticipant(room_id=room.id, user_id=admin.id)
    db.add(p)
```

To:
```python
for teacher in teachers:
    p = ChatParticipant(room_id=room.id, user_id=teacher.id)
    db.add(p)
    participants_added.append(teacher)
# Add DOS
admins = db.query(User).filter(User.role == "admin").all()
for admin in admins:
    p = ChatParticipant(room_id=room.id, user_id=admin.id)
    db.add(p)
    participants_added.append(admin)
```

### 4. Add notification sending code

BEFORE the `db.commit()` line, add:
```python
# Send notifications if enabled
if notify_participants:
    for participant_user in participants_added:
        notification = Notification(
            user_id=participant_user.id,
            title=f"📢 Added to Chat: {name}",
            message=f"You've been added to a new chat room '{name}'. Start chatting now!",
            type="chat_room_added"
        )
        db.add(notification)
```

### 5. Update return statement

Change:
```python
return {"id": room.id, "name": room.name, "room_type": room.room_type}
```

To:
```python
return {"id": room.id, "name": room.name, "room_type": room.room_type, "participants_added": len(participants_added)}
```

## After Making Changes

1. Save main.py
2. Restart the backend server
3. Test by creating a new room
4. Check student notifications

## Expected Result

When admin/teacher creates a room:
- All matching students receive notification: "📢 Added to Chat: [Room Name]"
- Notification appears in their notification bell
- Students can click to open chat
