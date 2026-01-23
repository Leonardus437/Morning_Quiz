# 💬 Real-Time Knowledge Hub Chat System

## Overview
A complete real-time chat system for students, teachers, and DOS to exchange knowledge, resources, and ideas - all under DOS supervision and control.

## Features

### 🎯 Core Features
- ✅ **Real-time messaging** (2-second polling)
- ✅ **Multiple room types** (Student-Student, Student-Teacher, Teacher-Teacher, Teacher-DOS)
- ✅ **Department & Level filtering** for students
- ✅ **Message history** with sender identification
- ✅ **Role-based access control**
- ✅ **DOS moderation** (flag messages, block users)
- ✅ **Floating chat button** (non-intrusive, always accessible)
- ✅ **Separate from anti-cheat** (doesn't interfere with quizzes)

### 👥 Room Types

#### 1. Student-to-Student 👥
- **Who**: Students from same department & level
- **Purpose**: Peer learning, study groups, resource sharing
- **Access**: All students in that dept/level auto-added
- **Example**: "SWD Level 5 Study Group"

#### 2. Student-to-Teacher 👨🎓
- **Who**: Students + Teachers from same department
- **Purpose**: Ask questions, get help, clarify concepts
- **Access**: Students from dept/level + teachers teaching that dept
- **Example**: "SWD Level 5 Q&A"

#### 3. Teacher-to-Teacher 👨🏫
- **Who**: All teachers
- **Purpose**: Share teaching resources, discuss pedagogy
- **Access**: All teachers auto-added
- **Example**: "Teachers Lounge"

#### 4. Teacher-to-DOS 🏛️
- **Who**: Teachers + DOS/Admin
- **Purpose**: Administrative discussions, policy updates
- **Access**: All teachers + DOS auto-added
- **Example**: "Staff Communication"

## User Guide

### For Students 📚

#### Accessing Chat
1. Look for the **floating chat button** (💬) in bottom-right corner
2. Click to open Knowledge Hub
3. See all available chat rooms for your department/level

#### Creating a Room
1. Click "+ New Room"
2. Choose room type:
   - **Students Only**: Chat with classmates
   - **Students & Teachers**: Get help from teachers
3. Select your department and level
4. Give it a name (e.g., "Python Study Group")
5. Click "Create"

#### Sending Messages
1. Select a room from the list
2. Type your message in the input box
3. Press "Send 📤" or hit Enter
4. Messages appear instantly (2-second refresh)

#### What You Can Share
- ✅ Study tips and techniques
- ✅ Resource links (YouTube, articles, tutorials)
- ✅ Code snippets and examples
- ✅ Questions and answers
- ✅ Project ideas and collaboration
- ✅ Exam preparation strategies

### For Teachers 👨🏫

#### Accessing Chat
1. Click the **floating chat button** (💬)
2. See all rooms you're part of
3. Create new rooms for your classes

#### Creating Rooms
1. Click "+ New Room"
2. Choose room type:
   - **Students & Teachers**: For class discussions
   - **Teachers Only**: For staff collaboration
   - **Teachers & DOS**: For administrative matters
3. Select department/level if applicable
4. Name the room appropriately
5. Click "Create"

#### Monitoring Discussions
- View all messages in real-time
- Identify students by name and role badge
- Answer questions and provide guidance
- Share resources and links
- Flag inappropriate content for DOS review

### For DOS/Admin 🏛️

#### Full Oversight
- **View all rooms**: Access every chat room in the system
- **Monitor all messages**: See all conversations
- **Review flagged content**: Check messages flagged by users
- **Block users**: Remove disruptive users from rooms
- **Delete messages**: Remove inappropriate content

#### Moderation Tools
1. **Flag Message**: Any user can flag inappropriate content
2. **Review Flagged**: DOS sees all flagged messages in dashboard
3. **Block User**: DOS can block users from specific rooms
4. **Delete Message**: DOS can delete any message

#### Accessing Moderation
1. Open chat
2. Click on flagged messages notification
3. Review content
4. Take action (block user, delete message, or dismiss)

## Technical Details

### Backend API Endpoints

```
GET  /chat/rooms                          - Get all accessible rooms
POST /chat/rooms                          - Create new room
GET  /chat/rooms/{room_id}/messages       - Get messages from room
POST /chat/rooms/{room_id}/messages       - Send message to room
DELETE /chat/messages/{message_id}        - Delete message
POST /chat/messages/{message_id}/flag     - Flag message for review
POST /chat/rooms/{room_id}/block-user/{user_id} - Block user (DOS only)
GET  /chat/flagged-messages               - Get flagged messages (DOS only)
```

### Database Schema

#### chat_rooms
- id, name, room_type, department, level
- is_active, created_by, created_at

#### chat_messages
- id, room_id, sender_id, message, message_type
- is_deleted, is_flagged, created_at

#### chat_participants
- id, room_id, user_id, is_blocked, joined_at

### Real-Time Updates
- **Polling interval**: 2 seconds
- **Message limit**: Last 50 messages per room
- **Auto-scroll**: New messages scroll to bottom
- **Unread indicators**: Red badge on rooms with new messages

## Integration

### Adding to Existing Pages

The chat system is **completely separate** from existing functionality:

1. **No interference with quizzes**: Chat is disabled during active quiz taking
2. **Floating button**: Always accessible but non-intrusive
3. **Modal overlay**: Opens on top of current page
4. **Independent state**: Doesn't affect quiz timers or anti-cheat

### Adding Chat Button to Any Page

```svelte
<script>
  import FloatingChatButton from '$lib/FloatingChatButton.svelte';
</script>

<!-- Your page content -->

<FloatingChatButton />
```

That's it! The button appears automatically for logged-in users.

## Security & Privacy

### Access Control
- ✅ **Role-based**: Students, Teachers, DOS have different permissions
- ✅ **Room-based**: Users only see rooms they're part of
- ✅ **Department filtering**: Students only join rooms for their dept/level
- ✅ **Authentication required**: Must be logged in to access chat

### DOS Supervision
- ✅ **Full visibility**: DOS sees all rooms and messages
- ✅ **Moderation tools**: Flag, block, delete capabilities
- ✅ **Audit trail**: All messages timestamped with sender info
- ✅ **User blocking**: Can remove disruptive users

### Content Guidelines
- ❌ No inappropriate language
- ❌ No spam or harassment
- ❌ No sharing of quiz answers during active quizzes
- ✅ Educational content only
- ✅ Respectful communication
- ✅ Constructive collaboration

## Benefits

### For Students
- 📚 **Peer learning**: Learn from classmates
- 🤝 **Collaboration**: Work together on projects
- 💡 **Quick help**: Get answers from teachers instantly
- 🔗 **Resource sharing**: Share useful links and materials
- 🎯 **Focused groups**: Department/level-specific discussions

### For Teachers
- 👨🎓 **Extended office hours**: Help students anytime
- 📢 **Announcements**: Quick updates to classes
- 🤝 **Collaboration**: Share resources with other teachers
- 📊 **Engagement**: Monitor student discussions
- 💬 **Direct communication**: Answer questions in real-time

### For DOS
- 🏛️ **Oversight**: Monitor all communications
- 🛡️ **Safety**: Ensure appropriate content
- 📊 **Insights**: Understand student/teacher needs
- 🔧 **Control**: Moderate and manage discussions
- 📢 **Communication**: Direct channel to all staff

## Best Practices

### Creating Effective Rooms
- ✅ Use clear, descriptive names
- ✅ Specify purpose in room name
- ✅ Keep rooms focused on specific topics
- ✅ Create separate rooms for different subjects

### Messaging Etiquette
- ✅ Be respectful and professional
- ✅ Stay on topic
- ✅ Use proper grammar and spelling
- ✅ Cite sources when sharing information
- ✅ Ask before sharing personal contact info

### For Teachers
- ✅ Set clear expectations for chat use
- ✅ Respond to student questions promptly
- ✅ Share high-quality resources
- ✅ Encourage peer-to-peer learning
- ✅ Monitor for off-topic discussions

## Troubleshooting

### Messages not appearing?
- Check internet connection
- Refresh the page
- Ensure you're in the correct room
- Wait 2 seconds for auto-refresh

### Can't create a room?
- Ensure you've filled all required fields
- Check you have permission for that room type
- Verify department/level selection

### Blocked from a room?
- Contact DOS/Admin for review
- Check if you violated content guidelines
- Request unblock if it was a mistake

## Future Enhancements

Potential additions (not yet implemented):
- 📎 File attachments
- 🖼️ Image sharing
- 🔔 Push notifications
- 🔍 Message search
- 📌 Pinned messages
- 👍 Message reactions
- 📊 Chat analytics for DOS

## Support

For issues or questions:
1. Contact your teacher
2. Reach out to DOS via Teacher-DOS chat
3. Check this documentation

---

**Remember**: The Knowledge Hub is for learning and collaboration. Use it wisely, respectfully, and productively! 🎓✨
