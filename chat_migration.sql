-- ============================================================================
-- CHAT SYSTEM DATABASE MIGRATION
-- Version: 1.0.0
-- Date: 2025-01-XX
-- Description: Add real-time group chat functionality
-- ============================================================================

-- 1. CHAT GROUPS TABLE
CREATE TABLE IF NOT EXISTS chat_groups (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    group_type VARCHAR(50) NOT NULL CHECK (group_type IN ('class', 'school', 'trade', 'level', 'custom')),
    
    -- Filters for auto-groups
    school_id INTEGER REFERENCES schools(id) ON DELETE CASCADE,
    trade_id INTEGER REFERENCES trades(id) ON DELETE CASCADE,
    level VARCHAR(20),
    department VARCHAR(100),
    
    -- Metadata
    created_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    is_active BOOLEAN DEFAULT true,
    avatar_url TEXT,
    member_count INTEGER DEFAULT 0,
    last_message_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Unique constraint for auto-groups (prevent duplicates)
CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_auto_group 
ON chat_groups (group_type, COALESCE(school_id, 0), COALESCE(trade_id, 0), COALESCE(level, ''), COALESCE(department, ''))
WHERE group_type IN ('class', 'school', 'trade', 'level');

-- Index for faster queries
CREATE INDEX IF NOT EXISTS idx_chat_groups_type ON chat_groups(group_type);
CREATE INDEX IF NOT EXISTS idx_chat_groups_school ON chat_groups(school_id) WHERE school_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_chat_groups_trade ON chat_groups(trade_id) WHERE trade_id IS NOT NULL;


-- 2. GROUP MEMBERS TABLE
CREATE TABLE IF NOT EXISTS chat_group_members (
    id SERIAL PRIMARY KEY,
    group_id INTEGER NOT NULL REFERENCES chat_groups(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(20) DEFAULT 'member' CHECK (role IN ('admin', 'moderator', 'member')),
    
    -- Status
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_read_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_muted BOOLEAN DEFAULT false,
    notification_enabled BOOLEAN DEFAULT true,
    
    UNIQUE(group_id, user_id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_group_members_group ON chat_group_members(group_id);
CREATE INDEX IF NOT EXISTS idx_group_members_user ON chat_group_members(user_id);
CREATE INDEX IF NOT EXISTS idx_group_members_unread ON chat_group_members(user_id, last_read_at);


-- 3. MESSAGES TABLE
CREATE TABLE IF NOT EXISTS chat_messages (
    id SERIAL PRIMARY KEY,
    group_id INTEGER NOT NULL REFERENCES chat_groups(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    
    -- Message content
    message_text TEXT,
    message_type VARCHAR(20) DEFAULT 'text' CHECK (message_type IN ('text', 'image', 'file', 'system', 'announcement')),
    
    -- File attachments
    file_url TEXT,
    file_name VARCHAR(255),
    file_size INTEGER,
    file_type VARCHAR(50),
    
    -- Reply/Thread
    reply_to_id INTEGER REFERENCES chat_messages(id) ON DELETE SET NULL,
    
    -- Status
    is_edited BOOLEAN DEFAULT false,
    is_deleted BOOLEAN DEFAULT false,
    edited_at TIMESTAMP,
    deleted_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for fast message retrieval
CREATE INDEX IF NOT EXISTS idx_messages_group_created ON chat_messages(group_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_messages_user ON chat_messages(user_id) WHERE user_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_messages_reply ON chat_messages(reply_to_id) WHERE reply_to_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_messages_active ON chat_messages(group_id, is_deleted, created_at DESC) WHERE is_deleted = false;


-- 4. MESSAGE REACTIONS TABLE
CREATE TABLE IF NOT EXISTS chat_message_reactions (
    id SERIAL PRIMARY KEY,
    message_id INTEGER NOT NULL REFERENCES chat_messages(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    reaction VARCHAR(10) NOT NULL, -- emoji: '👍', '❤️', '😂', '🎉', '🔥'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(message_id, user_id, reaction)
);

-- Index for fast reaction queries
CREATE INDEX IF NOT EXISTS idx_reactions_message ON chat_message_reactions(message_id);
CREATE INDEX IF NOT EXISTS idx_reactions_user ON chat_message_reactions(user_id);


-- 5. MESSAGE READ STATUS TABLE
CREATE TABLE IF NOT EXISTS chat_message_reads (
    id SERIAL PRIMARY KEY,
    message_id INTEGER NOT NULL REFERENCES chat_messages(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    read_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(message_id, user_id)
);

-- Index for read status queries
CREATE INDEX IF NOT EXISTS idx_reads_message ON chat_message_reads(message_id);
CREATE INDEX IF NOT EXISTS idx_reads_user ON chat_message_reads(user_id);


-- 6. TYPING INDICATORS TABLE (temporary status)
CREATE TABLE IF NOT EXISTS chat_typing_status (
    id SERIAL PRIMARY KEY,
    group_id INTEGER NOT NULL REFERENCES chat_groups(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP + INTERVAL '10 seconds'),
    
    UNIQUE(group_id, user_id)
);

-- Index for active typing status
CREATE INDEX IF NOT EXISTS idx_typing_group ON chat_typing_status(group_id, expires_at);


-- 7. USER ONLINE STATUS TABLE
CREATE TABLE IF NOT EXISTS user_online_status (
    user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    is_online BOOLEAN DEFAULT false,
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    socket_id VARCHAR(100),
    device_info JSONB,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for online users
CREATE INDEX IF NOT EXISTS idx_online_users ON user_online_status(is_online, last_seen DESC) WHERE is_online = true;


-- 8. CHAT NOTIFICATIONS TABLE
CREATE TABLE IF NOT EXISTS chat_notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    group_id INTEGER REFERENCES chat_groups(id) ON DELETE CASCADE,
    message_id INTEGER REFERENCES chat_messages(id) ON DELETE CASCADE,
    
    notification_type VARCHAR(50) NOT NULL, -- 'new_message', 'mention', 'reaction', 'group_invite'
    title VARCHAR(200),
    body TEXT,
    
    is_read BOOLEAN DEFAULT false,
    read_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for user notifications
CREATE INDEX IF NOT EXISTS idx_notifications_user ON chat_notifications(user_id, is_read, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_notifications_unread ON chat_notifications(user_id, created_at DESC) WHERE is_read = false;


-- ============================================================================
-- TRIGGERS FOR AUTOMATIC UPDATES
-- ============================================================================

-- Update group member count when member added/removed
CREATE OR REPLACE FUNCTION update_group_member_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE chat_groups 
        SET member_count = member_count + 1,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = NEW.group_id;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE chat_groups 
        SET member_count = GREATEST(member_count - 1, 0),
            updated_at = CURRENT_TIMESTAMP
        WHERE id = OLD.group_id;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_member_count
AFTER INSERT OR DELETE ON chat_group_members
FOR EACH ROW EXECUTE FUNCTION update_group_member_count();


-- Update last_message_at when new message sent
CREATE OR REPLACE FUNCTION update_group_last_message()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE chat_groups 
    SET last_message_at = NEW.created_at,
        updated_at = CURRENT_TIMESTAMP
    WHERE id = NEW.group_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_last_message
AFTER INSERT ON chat_messages
FOR EACH ROW EXECUTE FUNCTION update_group_last_message();


-- Clean up expired typing indicators
CREATE OR REPLACE FUNCTION cleanup_expired_typing()
RETURNS void AS $$
BEGIN
    DELETE FROM chat_typing_status 
    WHERE expires_at < CURRENT_TIMESTAMP;
END;
$$ LANGUAGE plpgsql;


-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- Get unread message count for user in group
CREATE OR REPLACE FUNCTION get_unread_count(p_user_id INTEGER, p_group_id INTEGER)
RETURNS INTEGER AS $$
DECLARE
    v_last_read TIMESTAMP;
    v_count INTEGER;
BEGIN
    -- Get user's last read timestamp
    SELECT last_read_at INTO v_last_read
    FROM chat_group_members
    WHERE user_id = p_user_id AND group_id = p_group_id;
    
    -- Count messages after last read
    SELECT COUNT(*) INTO v_count
    FROM chat_messages
    WHERE group_id = p_group_id 
      AND created_at > COALESCE(v_last_read, '1970-01-01'::TIMESTAMP)
      AND user_id != p_user_id
      AND is_deleted = false;
    
    RETURN COALESCE(v_count, 0);
END;
$$ LANGUAGE plpgsql;


-- Mark messages as read
CREATE OR REPLACE FUNCTION mark_messages_read(p_user_id INTEGER, p_group_id INTEGER)
RETURNS void AS $$
BEGIN
    -- Update last_read_at for user in group
    UPDATE chat_group_members
    SET last_read_at = CURRENT_TIMESTAMP
    WHERE user_id = p_user_id AND group_id = p_group_id;
    
    -- Insert read receipts for unread messages
    INSERT INTO chat_message_reads (message_id, user_id, read_at)
    SELECT m.id, p_user_id, CURRENT_TIMESTAMP
    FROM chat_messages m
    LEFT JOIN chat_message_reads r ON r.message_id = m.id AND r.user_id = p_user_id
    WHERE m.group_id = p_group_id 
      AND m.user_id != p_user_id
      AND r.id IS NULL
      AND m.is_deleted = false
    ON CONFLICT (message_id, user_id) DO NOTHING;
END;
$$ LANGUAGE plpgsql;


-- ============================================================================
-- INITIAL DATA / SAMPLE GROUPS (Optional)
-- ============================================================================

-- Create a general announcement group for all users
INSERT INTO chat_groups (name, description, group_type, created_by, is_active)
VALUES ('General Announcements', 'System-wide announcements and updates', 'custom', 1, true)
ON CONFLICT DO NOTHING;


-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================

-- Verify tables created
DO $$
DECLARE
    table_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO table_count
    FROM information_schema.tables
    WHERE table_schema = 'public'
      AND table_name IN (
          'chat_groups', 'chat_group_members', 'chat_messages',
          'chat_message_reactions', 'chat_message_reads',
          'chat_typing_status', 'user_online_status', 'chat_notifications'
      );
    
    IF table_count = 8 THEN
        RAISE NOTICE '✅ Chat system migration completed successfully! All 8 tables created.';
    ELSE
        RAISE WARNING '⚠️ Migration incomplete. Expected 8 tables, found %', table_count;
    END IF;
END $$;
