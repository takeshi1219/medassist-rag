-- MedAssist RAG Database Initialization Script
-- Run this script to set up the initial database schema

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create enum types
CREATE TYPE user_role AS ENUM ('doctor', 'nurse', 'pharmacist', 'admin');
CREATE TYPE query_type AS ENUM ('chat', 'drug_check', 'code_lookup', 'search');
CREATE TYPE severity_level AS ENUM ('none', 'mild', 'moderate', 'severe', 'contraindicated');

-- Users table (healthcare providers)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    role user_role NOT NULL DEFAULT 'doctor',
    organization VARCHAR(255),
    license_number VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index on email for fast lookups
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Query logs for audit
CREATE TABLE IF NOT EXISTS query_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    query_text TEXT NOT NULL,
    response_text TEXT,
    sources JSONB,
    query_type query_type NOT NULL,
    response_time_ms INTEGER,
    model_used VARCHAR(100),
    language VARCHAR(10) DEFAULT 'en',
    conversation_id VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for query logs
CREATE INDEX IF NOT EXISTS idx_query_logs_user_id ON query_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_query_logs_created_at ON query_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_query_logs_conversation_id ON query_logs(conversation_id);
CREATE INDEX IF NOT EXISTS idx_query_logs_user_created ON query_logs(user_id, created_at DESC);

-- Saved/bookmarked queries
CREATE TABLE IF NOT EXISTS saved_queries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    query_log_id UUID REFERENCES query_logs(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for saved queries
CREATE INDEX IF NOT EXISTS idx_saved_queries_user_id ON saved_queries(user_id);

-- Drug interactions cache
CREATE TABLE IF NOT EXISTS drug_interactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    drug_a VARCHAR(255) NOT NULL,
    drug_b VARCHAR(255) NOT NULL,
    severity severity_level NOT NULL,
    description TEXT NOT NULL,
    mechanism TEXT,
    management TEXT,
    clinical_effects JSONB,
    source VARCHAR(255),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(drug_a, drug_b)
);

-- Create index for drug interactions
CREATE INDEX IF NOT EXISTS idx_drug_interactions_drugs ON drug_interactions(drug_a, drug_b);

-- Medical codes cache
CREATE TABLE IF NOT EXISTS medical_codes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code_type VARCHAR(50) NOT NULL,
    code VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    description_ja TEXT,
    category VARCHAR(255),
    parent_code VARCHAR(100),
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(code_type, code)
);

-- Create indexes for medical codes
CREATE INDEX IF NOT EXISTS idx_medical_codes_type_code ON medical_codes(code_type, code);
CREATE INDEX IF NOT EXISTS idx_medical_codes_search ON medical_codes USING gin(to_tsvector('english', description));

-- Sessions table for Redis-backed sessions (optional)
CREATE TABLE IF NOT EXISTS sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_expires_at ON sessions(expires_at);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_drug_interactions_updated_at
    BEFORE UPDATE ON drug_interactions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Insert demo user (password: demo123)
INSERT INTO users (email, hashed_password, name, role, organization, license_number)
VALUES (
    'demo@medassist.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.VTtYNvMmDVeRiO',
    'Dr. Demo User',
    'doctor',
    'Demo Hospital',
    'MD123456'
) ON CONFLICT (email) DO NOTHING;

-- Grant permissions (adjust as needed for your setup)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO medassist_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO medassist_user;

COMMENT ON TABLE users IS 'Healthcare provider user accounts';
COMMENT ON TABLE query_logs IS 'Audit log for all queries made to the system';
COMMENT ON TABLE saved_queries IS 'User bookmarked/saved queries';
COMMENT ON TABLE drug_interactions IS 'Cached drug interaction information';
COMMENT ON TABLE medical_codes IS 'Cached medical codes (ICD-10, SNOMED-CT)';

