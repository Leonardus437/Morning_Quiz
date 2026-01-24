# Chat System & Class Teacher Guide

## 🎉 New Features Implemented

### 1. **Floating Chat Widget** (Bottom-Left Corner)
- **Location**: Bottom-left corner of every page
- **Appearance**: Beautiful gradient blue-purple button with chat icon
- **Visibility**: Appears for all logged-in users (students, teachers, admin)
- **Real-time**: Messages update every 2 seconds automatically

### 2. **Class Teacher Assignment** (Admin Panel)
- **Access**: Admin Dashboard → "Class Teachers" tab
- **Purpose**: Assign a teacher as class teacher for a specific department and level
- **Benefits**: 
  - Class teachers automatically get added to class chat rooms
  - Better class management and communication
  - Teachers receive notifications when assigned

### 3. **Real-Time Chat System**
- **Multiple Room Types**:
  - 👥 **Student-Student**: Only students from same department/level
  - 👨‍🎓 **Student-Teacher**: Students + Teachers + Class Teacher for a class
  - 👨‍🏫 **Teacher-Teacher**: All teachers can communicate
  - 🏛️ **Teacher-DOS**: Teachers and DOS/Admin communication

## 📋 How to Use

### For Admin (DOS):

#### Assign Class Teacher:
1. Login to Admin Dashboard
2. Click "Class Teachers" tab
3. Select:
   - Teacher name
   - Department
   - Level
4. Click "Assign Class Teacher"
5. Teacher will receive a notification

#### Create Class Chat Room:
1. Click the chat button (bottom-left)
2. Click "+ New Room"
3. Enter room name (e.g., "L5 Software Development Class")
4. Select room type: "Students & Teachers"
5. Select Department and Level
6. Click "Create"
7. **Automatic**: All students from that class + teachers + class teacher will be added automatically!

### For Teachers:

#### View Assigned Class:
1. Login to Teacher Dashboard
2. Check notifications for class teacher assignment
3. Access chat to see your class room

#### Create Chat Room:
1. Click chat button (bottom-left)
2. Click "+ New Room"
3. Choose room type:
   - "Students & Teachers" - for your class
   - "Teachers Only" - for teacher discussions
   - "Teachers & DOS" - to communicate with admin
4. Fill in details and create

### For Students:

#### Join Class Chat:
1. Click chat button (bottom-left)
2. You'll automatically see chat rooms for your department/level
3. Click on a room to start chatting
4. Send messages, view teacher responses in real-time

#### Create Student Group:
1. Click chat button (bottom-left)
2. Click "+ New Room"
3. Select "Students Only"
4. Choose your department and level
5. All classmates will be added automatically

## 🔥 Key Features

### Automatic Participant Addition:
- When creating a "Student-Teacher" room:
  - ✅ All students from selected department/level
  - ✅ All teachers teaching that department
  - ✅ Class teacher (if assigned)
  - ✅ Everyone gets notified!

### Real-Time Updates:
- Messages refresh every 2 seconds
- No need to reload page
- See who's online
- Instant notifications

### Smart Permissions:
- Students can only create student-student or student-teacher rooms
- Teachers can create all room types except DOS-only
- Admin can create any room type
- DOS can moderate all rooms

### Message Features:
- Text messages
- Sender name and role displayed
- Timestamp on each message
- Delete your own messages
- Flag inappropriate messages (DOS review)

## 🎯 Use Cases

### 1. Class Announcements:
- Teacher creates "L5 SWD Announcements" room
- All students automatically added
- Teacher posts important updates
- Students can ask questions

### 2. Study Groups:
- Students create "L5 SWD Study Group"
- All classmates automatically join
- Share notes, discuss assignments
- Collaborate on projects

### 3. Teacher Coordination:
- Teachers create "Teacher Lounge"
- Discuss teaching strategies
- Share resources
- Coordinate schedules

### 4. Admin Communication:
- DOS creates "Teachers & DOS" room
- Share school policies
- Get feedback from teachers
- Quick announcements

## 🔧 Technical Details

### Backend Endpoints:
- `GET /chat/rooms` - Get all accessible rooms
- `POST /chat/rooms` - Create new room
- `GET /chat/rooms/{id}/messages` - Get messages
- `POST /chat/rooms/{id}/messages` - Send message
- `POST /admin/assign-class-teacher` - Assign class teacher
- `GET /admin/class-teachers` - View assignments

### Database Tables:
- `chat_rooms` - Room information
- `chat_messages` - All messages
- `chat_participants` - Room membership
- `class_teachers` - Class teacher assignments

### Real-Time Polling:
- Messages poll every 2 seconds
- Automatic scroll to latest message
- Unread count indicator
- Connection status monitoring

## 🚀 Getting Started

### Quick Start for Admin:
```bash
1. Login as admin (username: admin, password: admin123)
2. Go to "Class Teachers" tab
3. Assign class teachers for each class
4. Click chat button (bottom-left)
5. Create class chat rooms
6. Done! Students and teachers can now chat
```

### Quick Start for Teachers:
```bash
1. Login to teacher portal
2. Check notifications for class assignment
3. Click chat button (bottom-left)
4. See your class rooms
5. Start communicating with students
```

### Quick Start for Students:
```bash
1. Login to student portal
2. Click chat button (bottom-left)
3. See available chat rooms
4. Join and start chatting
5. Create study groups with classmates
```

## 📱 Mobile Support

- Fully responsive design
- Works on phones and tablets
- Touch-friendly interface
- Optimized for small screens

## 🔒 Security & Moderation

### DOS Powers:
- View all chat rooms
- Flag inappropriate messages
- Block users from rooms
- Delete any message
- Monitor all conversations

### Privacy:
- Students only see their class rooms
- Teachers see relevant department rooms
- Messages are timestamped
- Sender identity always shown

## 💡 Tips & Best Practices

### For Admins:
- Assign class teachers at start of term
- Create official class rooms for each class
- Monitor flagged messages regularly
- Use descriptive room names

### For Teachers:
- Create separate rooms for different purposes
- Use announcements room for important info
- Encourage student participation
- Respond to questions promptly

### For Students:
- Use appropriate language
- Stay on topic
- Respect classmates and teachers
- Report inappropriate content

## 🐛 Troubleshooting

### Chat button not showing:
- Make sure you're logged in
- Refresh the page
- Clear browser cache

### Can't see messages:
- Check internet connection
- Verify you're a room participant
- Try leaving and rejoining room

### Room creation fails:
- Ensure department and level are selected
- Check you have permission for room type
- Verify room name is unique

## 📞 Support

For issues or questions:
- Contact DOS/Admin
- Check system logs
- Review this guide
- Test with sample data

## 🎓 Success!

Your TVET Quiz System now has:
✅ Beautiful chat widget in bottom-left
✅ Class teacher assignment system
✅ Automatic class-based chat groups
✅ Real-time messaging
✅ Smart participant management
✅ Full admin moderation tools

**Enjoy your enhanced communication system!** 💬🎉
