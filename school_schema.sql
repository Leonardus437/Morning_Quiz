-- School Management System Schema

-- Provinces table
CREATE TABLE IF NOT EXISTS provinces (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    code VARCHAR(10) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Districts table
CREATE TABLE IF NOT EXISTS districts (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(10) NOT NULL,
    province_id INTEGER REFERENCES provinces(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(name, province_id)
);

-- School types
CREATE TABLE IF NOT EXISTS school_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    abbreviation VARCHAR(10) UNIQUE NOT NULL,
    description TEXT
);

-- Schools table
CREATE TABLE IF NOT EXISTS schools (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    code VARCHAR(50) UNIQUE NOT NULL,
    school_type_id INTEGER REFERENCES school_types(id),
    district_id INTEGER REFERENCES districts(id),
    province_id INTEGER REFERENCES provinces(id),
    address TEXT,
    phone VARCHAR(20),
    email VARCHAR(100),
    is_reaccredited BOOLEAN DEFAULT false,
    accreditation_year VARCHAR(20),
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Trades/Programs table
CREATE TABLE IF NOT EXISTS trades (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    code VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    category VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- School trades junction (which trades each school offers)
CREATE TABLE IF NOT EXISTS school_trades (
    id SERIAL PRIMARY KEY,
    school_id INTEGER REFERENCES schools(id) ON DELETE CASCADE,
    trade_id INTEGER REFERENCES trades(id) ON DELETE CASCADE,
    levels JSONB,
    capacity INTEGER,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(school_id, trade_id)
);

-- Insert provinces
INSERT INTO provinces (name, code) VALUES 
('Kigali City', 'KGL'),
('Eastern Province', 'EST'),
('Northern Province', 'NTH'),
('Southern Province', 'STH'),
('Western Province', 'WST')
ON CONFLICT (code) DO NOTHING;

-- Insert school types
INSERT INTO school_types (name, abbreviation, description) VALUES 
('Technical Secondary School', 'TSS', 'Technical and vocational secondary schools'),
('Vocational Training Center', 'VTC', 'Vocational training centers'),
('Integrated Polytechnic Regional Center', 'IPRC', 'Integrated polytechnic regional centers')
ON CONFLICT (abbreviation) DO NOTHING;

-- Insert common trades
INSERT INTO trades (name, code, category) VALUES 
('Software Development', 'SWD', 'ICT'),
('Computer System and Architecture', 'CSA', 'ICT'),
('Computer Servicing and Maintenance', 'CSM', 'ICT'),
('Electronics and Telecommunication', 'ELT', 'ICT'),
('Land Surveying', 'LSV', 'Construction'),
('Building Construction', 'BDC', 'Construction'),
('Civil Engineering', 'CVE', 'Construction'),
('Plumbing', 'PLB', 'Construction'),
('Electrical Installation', 'ELI', 'Electrical'),
('Automotive Mechanics', 'AUM', 'Mechanical'),
('Welding and Metal Fabrication', 'WMF', 'Mechanical'),
('Hospitality Management', 'HSP', 'Hospitality'),
('Culinary Arts', 'CUL', 'Hospitality'),
('Agriculture', 'AGR', 'Agriculture'),
('Veterinary', 'VET', 'Agriculture')
ON CONFLICT (code) DO NOTHING;

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_schools_district ON schools(district_id);
CREATE INDEX IF NOT EXISTS idx_schools_province ON schools(province_id);
CREATE INDEX IF NOT EXISTS idx_schools_type ON schools(school_type_id);
CREATE INDEX IF NOT EXISTS idx_school_trades_school ON school_trades(school_id);
CREATE INDEX IF NOT EXISTS idx_school_trades_trade ON school_trades(trade_id);
CREATE INDEX IF NOT EXISTS idx_districts_province ON districts(province_id);
