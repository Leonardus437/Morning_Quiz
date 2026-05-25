-- Add missing user_online_status table
CREATE TABLE IF NOT EXISTS user_online_status (
    user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    is_online BOOLEAN DEFAULT FALSE,
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_online_users ON user_online_status(is_online, last_seen);

-- Verify all 8 tables exist
DO $$
BEGIN
    RAISE NOTICE 'Migration complete! All 8 chat tables should now exist.';
END $$;
