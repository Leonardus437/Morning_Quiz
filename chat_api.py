"""
Chat API Endpoints
Provides REST API for chat functionality
"""

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, Query, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import text, and_, or_, desc, func
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta
import json
import logging

from main import get_db, get_current_user, User, now
from chat_websocket import manager
from jose import jwt, JWTError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["Chat"])

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class GroupCreate(BaseModel):
    name: str
    description: Optional[str] = None
    group_type: str = 'custom'  # 'class', 'school', 'trade', 'level', 'custom'
    member_ids: List[int] = []

class GroupUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    avatar_url: Optional[str] = None

class MessageCreate(BaseModel):
    group_id: int
    message_text: str
    reply_to_id: Optional[int] = None
    message_type: str = 'text'

class MessageReaction(BaseModel):
    reaction: str  # emoji

class MessageEdit(BaseModel):
    message_text: str


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_or_create_auto_group(db: Session, group_type: str, **filters) -> dict:
    """Get or create automatic group based on filters"""
    
    # Build query
    query = """
        SELECT id, name, description, member_count, last_message_at
        FROM chat_groups
        WHERE group_type = :group_type
          AND is_active = true
    """
    params = {'group_type': group_type}
    
    # Add filters
    if 'school_id' in filters:
        query += " AND school_id = :school_id"
        params['school_id'] = filters['school_id']
    else:
        query += " AND school_id IS NULL"
    
    if 'trade_id' in filters:
        query += " AND trade_id = :trade_id"
        params['trade_id'] = filters['trade_id']
    else:
        query += " AND trade_id IS NULL"
    
    if 'level' in filters:
        query += " AND level = :level"
        params['level'] = filters['level']
    else:
        query += " AND level IS NULL"
    
    if 'department' in filters:
        query += " AND department = :department"
        params['department'] = filters['department']
    else:
        query += " AND department IS NULL"
    
    result = db.execute(text(query), params).fetchone()
    
    if result:
        return {
            'id': result[0],
            'name': result[1],
            'description': result[2],
            'member_count': result[3],
            'last_message_at': result[4].isoformat() if result[4] else None
        }
    
    # Create new group
    insert_query = """
        INSERT INTO chat_groups (name, description, group_type, school_id, trade_id, level, department, created_by)
        VALUES (:name, :description, :group_type, :school_id, :trade_id, :level, :department, :created_by)
        RETURNING id, name, description, member_count, last_message_at
    """
    
    insert_params = {
        'name': filters.get('name', f"{group_type.title()} Group"),
        'description': filters.get('description', f"Auto-generated {group_type} group"),
        'group_type': group_type,
        'school_id': filters.get('school_id'),
        'trade_id': filters.get('trade_id'),
        'level': filters.get('level'),
        'department': filters.get('department'),
        'created_by': filters.get('created_by', 1)
    }
    
    result = db.execute(text(insert_query), insert_params).fetchone()
    db.commit()
    
    return {
        'id': result[0],
        'name': result[1],
        'description': result[2],
        'member_count': result[3],
        'last_message_at': result[4].isoformat() if result[4] else None
    }


def auto_join_user_groups(db: Session, user: User):
    """Automatically join user to relevant groups"""
    groups_joined = []
    
    try:
        # 1. Class Group (Trade + Level)
        if user.trade_id and user.level:
            # Get trade name
            trade_result = db.execute(
                text("SELECT name FROM trades WHERE id = :tid"),
                {'tid': user.trade_id}
            ).fetchone()
            
            if trade_result:
                trade_name = trade_result[0]
                group = get_or_create_auto_group(
                    db,
                    group_type='class',
                    trade_id=user.trade_id,
                    level=user.level,
                    name=f"{trade_name} - {user.level}",
                    description=f"Class group for {trade_name} {user.level} students",
                    created_by=user.id
                )
                
                # Add user to group
                db.execute(text("""
                    INSERT INTO chat_group_members (group_id, user_id, role)
                    VALUES (:gid, :uid, 'member')
                    ON CONFLICT (group_id, user_id) DO NOTHING
                """), {'gid': group['id'], 'uid': user.id})
                
                groups_joined.append(group)
        
        # 2. School Group
        if user.school_id:
            school_result = db.execute(
                text("SELECT name FROM schools WHERE id = :sid"),
                {'sid': user.school_id}
            ).fetchone()
            
            if school_result:
                school_name = school_result[0]
                group = get_or_create_auto_group(
                    db,
                    group_type='school',
                    school_id=user.school_id,
                    name=f"{school_name} - All Students",
                    description=f"School-wide group for {school_name}",
                    created_by=user.id
                )
                
                db.execute(text("""
                    INSERT INTO chat_group_members (group_id, user_id, role)
                    VALUES (:gid, :uid, 'member')
                    ON CONFLICT (group_id, user_id) DO NOTHING
                """), {'gid': group['id'], 'uid': user.id})
                
                groups_joined.append(group)
        
        # 3. Trade Group (all levels)
        if user.trade_id:
            trade_result = db.execute(
                text("SELECT name FROM trades WHERE id = :tid"),
                {'tid': user.trade_id}
            ).fetchone()
            
            if trade_result:
                trade_name = trade_result[0]
                group = get_or_create_auto_group(
                    db,
                    group_type='trade',
                    trade_id=user.trade_id,
                    name=f"{trade_name} - All Levels",
                    description=f"Trade group for all {trade_name} students",
                    created_by=user.id
                )
                
                db.execute(text("""
                    INSERT INTO chat_group_members (group_id, user_id, role)
                    VALUES (:gid, :uid, 'member')
                    ON CONFLICT (group_id, user_id) DO NOTHING
                """), {'gid': group['id'], 'uid': user.id})
                
                groups_joined.append(group)
        
        # 4. Level Group (all trades)
        if user.level:
            group = get_or_create_auto_group(
                db,
                group_type='level',
                level=user.level,
                name=f"All {user.level} Students",
                description=f"Level group for all {user.level} students",
                created_by=user.id
            )
            
            db.execute(text("""
                INSERT INTO chat_group_members (group_id, user_id, role)
                VALUES (:gid, :uid, 'member')
                ON CONFLICT (group_id, user_id) DO NOTHING
            """), {'gid': group['id'], 'uid': user.id})
            
            groups_joined.append(group)
        
        db.commit()
        logger.info(f"✅ User {user.id} auto-joined {len(groups_joined)} groups")
        
    except Exception as e:
        logger.error(f"❌ Auto-join error for user {user.id}: {e}")
        db.rollback()
    
    return groups_joined


# ============================================================================
# WEBSOCKET ENDPOINT
# ============================================================================

@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """WebSocket connection for real-time chat"""
    
    user = None
    user_id = None
    
    try:
        # Verify JWT token
        from main import SECRET_KEY, ALGORITHM
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        
        if not username:
            await websocket.close(code=1008, reason="Invalid token")
            return
        
        # Get user
        user = db.query(User).filter(User.username == username).first()
        if not user:
            await websocket.close(code=1008, reason="User not found")
            return
        
        user_id = user.id
        
        # Connect user
        await manager.connect(websocket, user_id, {
            'username': user.username,
            'full_name': user.full_name,
            'role': user.role
        })
        
        # Update online status in database
        db.execute(text("""
            INSERT INTO user_online_status (user_id, is_online, last_seen)
            VALUES (:uid, true, :now)
            ON CONFLICT (user_id) DO UPDATE
            SET is_online = true, last_seen = :now, updated_at = :now
        """), {'uid': user_id, 'now': now()})
        db.commit()
        
        # Load user's groups into manager cache
        groups_result = db.execute(text("""
            SELECT DISTINCT g.id
            FROM chat_groups g
            JOIN chat_group_members m ON g.id = m.group_id
            WHERE m.user_id = :uid AND g.is_active = true
        """), {'uid': user_id}).fetchall()
        
        for (group_id,) in groups_result:
            # Load group members
            members_result = db.execute(text("""
                SELECT user_id FROM chat_group_members WHERE group_id = :gid
            """), {'gid': group_id}).fetchall()
            
            member_ids = [m[0] for m in members_result]
            manager.load_group_members(group_id, member_ids)
        
        # Send initial connection success
        await websocket.send_json({
            'type': 'connected',
            'user_id': user_id,
            'timestamp': now().isoformat(),
            'message': 'Connected to chat server'
        })
        
        # Listen for messages
        while True:
            data = await websocket.receive_json()
            
            message_type = data.get('type')
            
            if message_type == 'message':
                # Handle new message
                group_id = data.get('group_id')
                text_content = data.get('text', '').strip()
                reply_to_id = data.get('reply_to_id')
                
                if not text_content or not group_id:
                    continue
                
                # Save message to database
                result = db.execute(text("""
                    INSERT INTO chat_messages (group_id, user_id, message_text, message_type, reply_to_id)
                    VALUES (:gid, :uid, :text, 'text', :reply)
                    RETURNING id, created_at
                """), {
                    'gid': group_id,
                    'uid': user_id,
                    'text': text_content,
                    'reply': reply_to_id
                }).fetchone()
                
                db.commit()
                
                message_id, created_at = result
                
                # Broadcast to group
                await manager.broadcast_to_group(group_id, {
                    'type': 'new_message',
                    'message': {
                        'id': message_id,
                        'group_id': group_id,
                        'user_id': user_id,
                        'username': user.username,
                        'full_name': user.full_name,
                        'message_text': text_content,
                        'message_type': 'text',
                        'reply_to_id': reply_to_id,
                        'created_at': created_at.isoformat(),
                        'reactions': []
                    }
                })
            
            elif message_type == 'typing':
                # Handle typing indicator
                group_id = data.get('group_id')
                is_typing = data.get('is_typing', True)
                
                if group_id:
                    await manager.handle_typing(user_id, group_id, is_typing)
            
            elif message_type == 'read':
                # Mark messages as read
                group_id = data.get('group_id')
                
                if group_id:
                    db.execute(text("SELECT mark_messages_read(:uid, :gid)"), {
                        'uid': user_id,
                        'gid': group_id
                    })
                    db.commit()
            
            elif message_type == 'ping':
                # Heartbeat
                await websocket.send_json({'type': 'pong'})
    
    except WebSocketDisconnect:
        logger.info(f"🔌 User {user_id} disconnected")
    
    except JWTError:
        logger.error("❌ Invalid JWT token")
        await websocket.close(code=1008, reason="Invalid token")
    
    except Exception as e:
        logger.error(f"❌ WebSocket error: {e}")
    
    finally:
        if user_id:
            # Disconnect user
            manager.disconnect(websocket, user_id)
            
            # Update online status
            try:
                db.execute(text("""
                    UPDATE user_online_status
                    SET is_online = false, last_seen = :now, updated_at = :now
                    WHERE user_id = :uid
                """), {'uid': user_id, 'now': now()})
                db.commit()
            except:
                pass


# ============================================================================
# REST API ENDPOINTS
# ============================================================================

@router.get("/groups")
async def get_user_groups(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all groups user is member of"""
    
    # Auto-join user to groups if not already
    auto_join_user_groups(db, current_user)
    
    result = db.execute(text("""
        SELECT 
            g.id, g.name, g.description, g.group_type, g.avatar_url,
            g.member_count, g.last_message_at, g.created_at,
            m.role, m.is_muted, m.last_read_at,
            get_unread_count(:uid, g.id) as unread_count
        FROM chat_groups g
        JOIN chat_group_members m ON g.id = m.group_id
        WHERE m.user_id = :uid AND g.is_active = true
        ORDER BY g.last_message_at DESC NULLS LAST, g.created_at DESC
    """), {'uid': current_user.id}).fetchall()
    
    groups = []
    for row in result:
        groups.append({
            'id': row[0],
            'name': row[1],
            'description': row[2],
            'group_type': row[3],
            'avatar_url': row[4],
            'member_count': row[5],
            'last_message_at': row[6].isoformat() if row[6] else None,
            'created_at': row[7].isoformat() if row[7] else None,
            'user_role': row[8],
            'is_muted': row[9],
            'last_read_at': row[10].isoformat() if row[10] else None,
            'unread_count': row[11] or 0
        })
    
    return {'groups': groups, 'total': len(groups)}


@router.post("/groups")
async def create_group(
    group: GroupCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new custom chat group"""
    
    if current_user.role not in ['teacher', 'admin']:
        raise HTTPException(status_code=403, detail="Only teachers and admins can create custom groups")
    
    # Create group
    result = db.execute(text("""
        INSERT INTO chat_groups (name, description, group_type, created_by)
        VALUES (:name, :desc, :type, :creator)
        RETURNING id, name, description, group_type, created_at
    """), {
        'name': group.name,
        'desc': group.description,
        'type': group.group_type,
        'creator': current_user.id
    }).fetchone()
    
    group_id = result[0]
    
    # Add creator as admin
    db.execute(text("""
        INSERT INTO chat_group_members (group_id, user_id, role)
        VALUES (:gid, :uid, 'admin')
    """), {'gid': group_id, 'uid': current_user.id})
    
    # Add members
    for member_id in group.member_ids:
        db.execute(text("""
            INSERT INTO chat_group_members (group_id, user_id, role)
            VALUES (:gid, :uid, 'member')
            ON CONFLICT (group_id, user_id) DO NOTHING
        """), {'gid': group_id, 'uid': member_id})
    
    db.commit()
    
    return {
        'id': result[0],
        'name': result[1],
        'description': result[2],
        'group_type': result[3],
        'created_at': result[4].isoformat(),
        'message': 'Group created successfully'
    }


@router.get("/groups/{group_id}/messages")
async def get_group_messages(
    group_id: int,
    limit: int = Query(50, le=100),
    before_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get messages for a group with pagination"""
    
    # Verify membership
    member_check = db.execute(text("""
        SELECT 1 FROM chat_group_members
        WHERE group_id = :gid AND user_id = :uid
    """), {'gid': group_id, 'uid': current_user.id}).fetchone()
    
    if not member_check:
        raise HTTPException(status_code=403, detail="Not a member of this group")
    
    # Build query
    query = """
        SELECT 
            m.id, m.user_id, m.message_text, m.message_type,
            m.file_url, m.file_name, m.reply_to_id,
            m.is_edited, m.created_at,
            u.username, u.full_name,
            (SELECT json_agg(json_build_object('reaction', r.reaction, 'count', COUNT(*)))
             FROM chat_message_reactions r
             WHERE r.message_id = m.id
             GROUP BY r.reaction) as reactions
        FROM chat_messages m
        LEFT JOIN users u ON m.user_id = u.id
        WHERE m.group_id = :gid AND m.is_deleted = false
    """
    
    params = {'gid': group_id, 'limit': limit}
    
    if before_id:
        query += " AND m.id < :before_id"
        params['before_id'] = before_id
    
    query += " ORDER BY m.created_at DESC LIMIT :limit"
    
    result = db.execute(text(query), params).fetchall()
    
    messages = []
    for row in result:
        messages.append({
            'id': row[0],
            'user_id': row[1],
            'message_text': row[2],
            'message_type': row[3],
            'file_url': row[4],
            'file_name': row[5],
            'reply_to_id': row[6],
            'is_edited': row[7],
            'created_at': row[8].isoformat(),
            'username': row[9],
            'full_name': row[10],
            'reactions': row[11] or []
        })
    
    # Reverse to get chronological order
    messages.reverse()
    
    return {'messages': messages, 'count': len(messages)}


@router.post("/messages")
async def send_message(
    message: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send message to group (REST endpoint, also handled via WebSocket)"""
    
    # Verify membership
    member_check = db.execute(text("""
        SELECT 1 FROM chat_group_members
        WHERE group_id = :gid AND user_id = :uid
    """), {'gid': message.group_id, 'uid': current_user.id}).fetchone()
    
    if not member_check:
        raise HTTPException(status_code=403, detail="Not a member of this group")
    
    # Save message
    result = db.execute(text("""
        INSERT INTO chat_messages (group_id, user_id, message_text, message_type, reply_to_id)
        VALUES (:gid, :uid, :text, :type, :reply)
        RETURNING id, created_at
    """), {
        'gid': message.group_id,
        'uid': current_user.id,
        'text': message.message_text,
        'type': message.message_type,
        'reply': message.reply_to_id
    }).fetchone()
    
    db.commit()
    
    message_id, created_at = result
    
    # Broadcast via WebSocket
    await manager.broadcast_to_group(message.group_id, {
        'type': 'new_message',
        'message': {
            'id': message_id,
            'group_id': message.group_id,
            'user_id': current_user.id,
            'username': current_user.username,
            'full_name': current_user.full_name,
            'message_text': message.message_text,
            'message_type': message.message_type,
            'reply_to_id': message.reply_to_id,
            'created_at': created_at.isoformat(),
            'reactions': []
        }
    })
    
    return {
        'id': message_id,
        'created_at': created_at.isoformat(),
        'message': 'Message sent successfully'
    }


@router.post("/messages/{message_id}/react")
async def react_to_message(
    message_id: int,
    reaction: MessageReaction,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add or remove reaction to message"""
    
    # Check if reaction exists
    existing = db.execute(text("""
        SELECT id FROM chat_message_reactions
        WHERE message_id = :mid AND user_id = :uid AND reaction = :react
    """), {'mid': message_id, 'uid': current_user.id, 'react': reaction.reaction}).fetchone()
    
    if existing:
        # Remove reaction
        db.execute(text("""
            DELETE FROM chat_message_reactions
            WHERE message_id = :mid AND user_id = :uid AND reaction = :react
        """), {'mid': message_id, 'uid': current_user.id, 'react': reaction.reaction})
        action = 'removed'
    else:
        # Add reaction
        db.execute(text("""
            INSERT INTO chat_message_reactions (message_id, user_id, reaction)
            VALUES (:mid, :uid, :react)
        """), {'mid': message_id, 'uid': current_user.id, 'react': reaction.reaction})
        action = 'added'
    
    db.commit()
    
    # Get group_id for broadcasting
    group_result = db.execute(text("""
        SELECT group_id FROM chat_messages WHERE id = :mid
    """), {'mid': message_id}).fetchone()
    
    if group_result:
        group_id = group_result[0]
        
        # Broadcast reaction update
        await manager.broadcast_to_group(group_id, {
            'type': 'reaction_update',
            'message_id': message_id,
            'user_id': current_user.id,
            'reaction': reaction.reaction,
            'action': action
        })
    
    return {'message': f'Reaction {action}', 'action': action}


@router.get("/online-users")
async def get_online_users(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of online users"""
    
    result = db.execute(text("""
        SELECT u.id, u.username, u.full_name, s.last_seen
        FROM user_online_status s
        JOIN users u ON s.user_id = u.id
        WHERE s.is_online = true
        ORDER BY u.full_name
    """)).fetchall()
    
    users = []
    for row in result:
        users.append({
            'id': row[0],
            'username': row[1],
            'full_name': row[2],
            'last_seen': row[3].isoformat() if row[3] else None
        })
    
    return {'online_users': users, 'count': len(users)}


@router.get("/stats")
async def get_chat_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get chat statistics"""
    
    stats = manager.get_stats()
    
    # Add database stats
    db_stats = db.execute(text("""
        SELECT 
            (SELECT COUNT(*) FROM chat_groups WHERE is_active = true) as total_groups,
            (SELECT COUNT(*) FROM chat_messages WHERE is_deleted = false) as total_messages,
            (SELECT COUNT(*) FROM user_online_status WHERE is_online = true) as db_online_users
    """)).fetchone()
    
    return {
        'websocket': stats,
        'database': {
            'total_groups': db_stats[0],
            'total_messages': db_stats[1],
            'online_users': db_stats[2]
        }
    }
