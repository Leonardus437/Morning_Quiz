-- CHAT SYSTEM DATABASE MIGRATION (Clean Version)
-- Run this to complete the migration

-- 4. MESSAGE REACTIONS TABLE (if not exists)
CREATE TABLE IF NOT EXISTS chat_message_reactions (
    id SERIAL PRIMARY KEY,
    message_id INTEGER NOT NULL REFERENCES chat_messages(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    reaction VARCHAR(10) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(message_id, user_id, reaction)
);

CREATE INDEX IF NOT EXISTS idx_reactions_message ON chat_message_reactions(message_id);
CREATE INDEX IF NOT EXISTS idx_reactions_user ON chat_message_reactions(user_id);

-- 5. MESSAGE READ STATUS TABLE (if not exists)
CREATE TABLE IF NOT EXISTS chat_message_reads (
    id SERIAL PRIMARY KEY,
    message_id INTEGER NOT NULL REFERENCES chat_messages(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    read_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(message_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_reads_message ON chat_message_reads(message_id);
CREATE INDEX IF NOT EXISTS idx_reads_user ON chat_message_reads(user_id);

-- 6. TYPING INDICATORS TABLE (if not exists)
CREATE TABLE IF NOT EXISTS chat_typing_status (
    id SERIAL PRIMARY KEY,
    group_id INTEGER NOT NULL REFERENCES chat_groups(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP + INTERVAL '10 seconds'),
    UNIQUE(group_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_typing_group ON chat_typing_status(group_id, expires_at);

-- 7. USER ONLINE STATUS TABLE (if not exists)
CREATE TABLE IF NOT EXISTS user_online_status (
    user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    is_online BOOLEAN DEFAULT false,
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    socket_id VARCHAR(100),
    device_info JSONB,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_online_users ON user_online_status(is_online, last_seen DESC) WHERE is_online = true;

-- 8. CHAT NOTIFICATIONS TABLE (if not exists)
CREATE TABLE IF NOT EXISTS chat_notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    group_id INTEGER REFERENCES chat_groups(id) ON DELETE CASCADE,
    message_id INTEGER REFERENCES chat_messages(id) ON DELETE CASCADE,
    notification_type VARCHAR(50) NOT NULL,
    title VARCHAR(200),
    body TEXT,
    is_read BOOLEAN DEFAULT false,
    read_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_notifications_user ON chat_notifications(user_id, is_read, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_notifications_unread ON chat_notifications(user_id, created_at DESC) WHERE is_read = false;

-- TRIGGERS (Create if not exists)
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

DROP TRIGGER IF EXISTS trigger_update_member_count ON chat_group_members;
CREATE TRIGGER trigger_update_member_count
AFTER INSERT OR DELETE ON chat_group_members
FOR EACH ROW EXECUTE FUNCTION update_group_member_count();

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

DROP TRIGGER IF EXISTS trigger_update_last_message ON chat_messages;
CREATE TRIGGER trigger_update_last_message
AFTER INSERT ON chat_messages
FOR EACH ROW EXECUTE FUNCTION update_group_last_message();

-- HELPER FUNCTIONS
CREATE OR REPLACE FUNCTION get_unread_count(p_user_id INTEGER, p_group_id INTEGER)
RETURNS INTEGER AS $$
DECLARE
    v_last_read TIMESTAMP;
    v_count INTEGER;
BEGIN
    SELECT last_read_at INTO v_last_read
    FROM chat_group_members
    WHERE user_id = p_user_id AND group_id = p_group_id;
    
    SELECT COUNT(*) INTO v_count
    FROM chat_messages
    WHERE group_id = p_group_id 
      AND created_at > COALESCE(v_last_read, '1970-01-01'::TIMESTAMP)
      AND user_id != p_user_id
      AND is_deleted = false;
    
    RETURN COALESCE(v_count, 0);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION mark_messages_read(p_user_id INTEGER, p_group_id INTEGER)
RETURNS void AS $$
BEGIN
    UPDATE chat_group_members
    SET last_read_at = CURRENT_TIMESTAMP
    WHERE user_id = p_user_id AND group_id = p_group_id;
    
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

-- Verify completion
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
        RAISE NOTICE 'SUCCESS: All 8 chat tables created!';
    ELSE
        RAISE WARNING 'INCOMPLETE: Expected 8 tables, found %', table_count;
    END IF;
END $$;
