-- Educational Materials System - Database Schema

-- Materials table
CREATE TABLE IF NOT EXISTS materials (
    id SERIAL PRIMARY KEY,
    title VARCHAR(300) NOT NULL,
    description TEXT,
    content TEXT NOT NULL,
    material_type VARCHAR(50) NOT NULL CHECK (material_type IN ('article', 'video', 'pdf', 'link', 'interactive', 'slides', 'document')),
    department VARCHAR(100) NOT NULL,
    level VARCHAR(20) NOT NULL,
    lesson_id INTEGER REFERENCES lessons(id) ON DELETE SET NULL,
    tags TEXT[],
    estimated_time INTEGER, -- in minutes
    is_published BOOLEAN DEFAULT true,
    created_by INTEGER REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Material interactions (views, likes, bookmarks, completions)
CREATE TABLE IF NOT EXISTS material_interactions (
    id SERIAL PRIMARY KEY,
    material_id INTEGER REFERENCES materials(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    interaction_type VARCHAR(20) NOT NULL CHECK (interaction_type IN ('view', 'like', 'bookmark', 'complete')),
    progress INTEGER DEFAULT 0 CHECK (progress >= 0 AND progress <= 100), -- completion percentage
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Material comments (for discussions)
CREATE TABLE IF NOT EXISTS material_comments (
    id SERIAL PRIMARY KEY,
    material_id INTEGER REFERENCES materials(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    comment_text TEXT NOT NULL,
    parent_id INTEGER REFERENCES material_comments(id) ON DELETE CASCADE, -- for threaded comments
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_materials_dept_level ON materials(department, level);
CREATE INDEX IF NOT EXISTS idx_materials_created_by ON materials(created_by);
CREATE INDEX IF NOT EXISTS idx_materials_published ON materials(is_published);
CREATE INDEX IF NOT EXISTS idx_material_interactions_material ON material_interactions(material_id);
CREATE INDEX IF NOT EXISTS idx_material_interactions_user ON material_interactions(user_id);
CREATE INDEX IF NOT EXISTS idx_material_comments_material ON material_comments(material_id);
