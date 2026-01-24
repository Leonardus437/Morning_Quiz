# Quick fix for chat room access
# Replace the get_chat_rooms function in main.py

@app.get("/chat/rooms")
def get_chat_rooms(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all chat rooms accessible to current user"""
    rooms = []
    
    if current_user.role == "admin":
        # DOS sees all rooms
        all_rooms = db.query(ChatRoom).filter(ChatRoom.is_active == True).all()
        for room in all_rooms:
            rooms.append({
                "id": room.id,
                "name": room.name,
                "room_type": room.room_type,
                "department": room.department,
                "level": room.level,
                "unread_count": 0
            })
    elif current_user.role == "teacher":
        # Teachers see all rooms they can access based on department
        all_rooms = db.query(ChatRoom).filter(ChatRoom.is_active == True).all()
        for room in all_rooms:
            can_access = False
            
            if room.room_type in ["teacher-teacher", "teacher-dos"]:
                can_access = True
            elif room.room_type in ["student-teacher", "student-student"]:
                # Teacher can access if they teach this department
                if current_user.departments and room.department in current_user.departments:
                    can_access = True
            
            if can_access:
                # Auto-add teacher as participant if not already
                participant = db.query(ChatParticipant).filter(
                    ChatParticipant.room_id == room.id,
                    ChatParticipant.user_id == current_user.id
                ).first()
                if not participant:
                    participant = ChatParticipant(room_id=room.id, user_id=current_user.id)
                    db.add(participant)
                    db.commit()
                
                rooms.append({
                    "id": room.id,
                    "name": room.name,
                    "room_type": room.room_type,
                    "department": room.department,
                    "level": room.level,
                    "unread_count": 0
                })
    else:  # student
        # Students see rooms for their department/level
        all_rooms = db.query(ChatRoom).filter(ChatRoom.is_active == True).all()
        for room in all_rooms:
            can_access = False
            
            if room.room_type in ["student-student", "student-teacher"]:
                # Student can access if same department and level
                if (room.department == current_user.department and 
                    room.level == current_user.level):
                    can_access = True
            
            if can_access:
                # Auto-add student as participant if not already
                participant = db.query(ChatParticipant).filter(
                    ChatParticipant.room_id == room.id,
                    ChatParticipant.user_id == current_user.id
                ).first()
                if not participant:
                    participant = ChatParticipant(room_id=room.id, user_id=current_user.id)
                    db.add(participant)
                    db.commit()
                
                rooms.append({
                    "id": room.id,
                    "name": room.name,
                    "room_type": room.room_type,
                    "department": room.department,
                    "level": room.level,
                    "unread_count": 0
                })
    
    return rooms