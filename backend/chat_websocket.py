"""
WebSocket Connection Manager for Real-Time Chat
Handles WebSocket connections, message broadcasting, and online status
"""

from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set, List, Optional
import json
import asyncio
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections for real-time chat"""
    
    def __init__(self):
        # user_id -> Set of WebSocket connections (multiple devices)
        self.active_connections: Dict[int, Set[WebSocket]] = {}
        
        # group_id -> Set of user_ids (for efficient broadcasting)
        self.group_members: Dict[int, Set[int]] = {}
        
        # user_id -> typing status per group
        self.typing_users: Dict[int, Dict[int, float]] = {}  # {user_id: {group_id: timestamp}}
        
        # Track connection metadata
        self.connection_metadata: Dict[WebSocket, dict] = {}
    
    
    async def connect(self, websocket: WebSocket, user_id: int, user_data: dict = None):
        """Accept new WebSocket connection"""
        try:
            await websocket.accept()
            
            # Add connection
            if user_id not in self.active_connections:
                self.active_connections[user_id] = set()
            self.active_connections[user_id].add(websocket)
            
            # Store metadata
            self.connection_metadata[websocket] = {
                'user_id': user_id,
                'connected_at': datetime.utcnow(),
                'user_data': user_data or {}
            }
            
            logger.info(f"✅ User {user_id} connected. Total connections: {len(self.active_connections[user_id])}")
            
            # Broadcast online status to relevant groups
            await self.broadcast_user_status(user_id, is_online=True)
            
        except Exception as e:
            logger.error(f"❌ Connection error for user {user_id}: {e}")
            raise
    
    
    def disconnect(self, websocket: WebSocket, user_id: int):
        """Remove WebSocket connection"""
        try:
            if user_id in self.active_connections:
                self.active_connections[user_id].discard(websocket)
                
                # Remove user entry if no more connections
                if not self.active_connections[user_id]:
                    del self.active_connections[user_id]
                    logger.info(f"🔴 User {user_id} fully disconnected")
                else:
                    logger.info(f"📱 User {user_id} disconnected from one device. Remaining: {len(self.active_connections[user_id])}")
            
            # Clean up metadata
            if websocket in self.connection_metadata:
                del self.connection_metadata[websocket]
            
            # Clean up typing status
            if user_id in self.typing_users:
                del self.typing_users[user_id]
            
        except Exception as e:
            logger.error(f"❌ Disconnect error for user {user_id}: {e}")
    
    
    async def send_to_user(self, user_id: int, message: dict):
        """Send message to specific user (all their devices)"""
        if user_id in self.active_connections:
            disconnected = set()
            
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.warning(f"⚠️ Failed to send to user {user_id}: {e}")
                    disconnected.add(connection)
            
            # Clean up dead connections
            for conn in disconnected:
                self.active_connections[user_id].discard(conn)
    
    
    async def broadcast_to_group(self, group_id: int, message: dict, exclude_user: int = None):
        """Broadcast message to all members of a group"""
        if group_id not in self.group_members:
            logger.warning(f"⚠️ Group {group_id} has no cached members")
            return
        
        sent_count = 0
        for user_id in self.group_members[group_id]:
            if user_id != exclude_user:
                await self.send_to_user(user_id, message)
                sent_count += 1
        
        logger.debug(f"📢 Broadcasted to {sent_count} users in group {group_id}")
    
    
    async def broadcast_user_status(self, user_id: int, is_online: bool):
        """Broadcast user online/offline status to their groups"""
        message = {
            'type': 'user_status',
            'user_id': user_id,
            'is_online': is_online,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Send to all groups user is member of
        for group_id, members in self.group_members.items():
            if user_id in members:
                await self.broadcast_to_group(group_id, message, exclude_user=user_id)
    
    
    def add_user_to_group(self, user_id: int, group_id: int):
        """Add user to group member cache"""
        if group_id not in self.group_members:
            self.group_members[group_id] = set()
        self.group_members[group_id].add(user_id)
    
    
    def remove_user_from_group(self, user_id: int, group_id: int):
        """Remove user from group member cache"""
        if group_id in self.group_members:
            self.group_members[group_id].discard(user_id)
    
    
    def load_group_members(self, group_id: int, member_ids: List[int]):
        """Load group members into cache"""
        self.group_members[group_id] = set(member_ids)
        logger.info(f"📋 Loaded {len(member_ids)} members for group {group_id}")
    
    
    async def handle_typing(self, user_id: int, group_id: int, is_typing: bool):
        """Handle typing indicator"""
        current_time = datetime.utcnow().timestamp()
        
        if is_typing:
            # Add/update typing status
            if user_id not in self.typing_users:
                self.typing_users[user_id] = {}
            self.typing_users[user_id][group_id] = current_time
        else:
            # Remove typing status
            if user_id in self.typing_users and group_id in self.typing_users[user_id]:
                del self.typing_users[user_id][group_id]
        
        # Broadcast typing status
        message = {
            'type': 'typing',
            'user_id': user_id,
            'group_id': group_id,
            'is_typing': is_typing,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        await self.broadcast_to_group(group_id, message, exclude_user=user_id)
    
    
    def get_online_users(self) -> List[int]:
        """Get list of currently online user IDs"""
        return list(self.active_connections.keys())
    
    
    def is_user_online(self, user_id: int) -> bool:
        """Check if user is currently online"""
        return user_id in self.active_connections
    
    
    def get_connection_count(self) -> int:
        """Get total number of active connections"""
        return sum(len(connections) for connections in self.active_connections.values())
    
    
    def get_stats(self) -> dict:
        """Get connection statistics"""
        return {
            'total_users_online': len(self.active_connections),
            'total_connections': self.get_connection_count(),
            'active_groups': len(self.group_members),
            'typing_users': sum(len(groups) for groups in self.typing_users.values())
        }
    
    
    async def cleanup_stale_typing(self, timeout_seconds: int = 10):
        """Clean up stale typing indicators (run periodically)"""
        current_time = datetime.utcnow().timestamp()
        stale_users = []
        
        for user_id, groups in self.typing_users.items():
            stale_groups = []
            for group_id, timestamp in groups.items():
                if current_time - timestamp > timeout_seconds:
                    stale_groups.append(group_id)
                    # Broadcast typing stopped
                    await self.handle_typing(user_id, group_id, is_typing=False)
            
            for group_id in stale_groups:
                del groups[group_id]
            
            if not groups:
                stale_users.append(user_id)
        
        # Clean up empty entries
        for user_id in stale_users:
            del self.typing_users[user_id]


# Global connection manager instance
manager = ConnectionManager()


# Background task to clean up stale typing indicators
async def typing_cleanup_task():
    """Background task to clean up stale typing indicators"""
    while True:
        try:
            await asyncio.sleep(5)  # Run every 5 seconds
            await manager.cleanup_stale_typing(timeout_seconds=10)
        except Exception as e:
            logger.error(f"❌ Typing cleanup error: {e}")
