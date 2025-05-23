-- Initialize Supabase Database for RecruitBot

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(256) NOT NULL,
    role VARCHAR(20) DEFAULT 'candidate',
    name VARCHAR(100),
    age INTEGER,
    experience INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Interviews Table
CREATE TABLE IF NOT EXISTS interviews (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) NOT NULL,
    job_role VARCHAR(100) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    result VARCHAR(20),
    score FLOAT,
    summary TEXT,
    evaluation_report TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- Questions Table
CREATE TABLE IF NOT EXISTS questions (
    id SERIAL PRIMARY KEY,
    interview_id INTEGER REFERENCES interviews(id) NOT NULL,
    text TEXT NOT NULL,
    category VARCHAR(50),
    type VARCHAR(20),
    answer TEXT,
    score FLOAT,
    feedback TEXT,
    "order" INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    answered_at TIMESTAMP
);

-- Create Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_interviews_user_id ON interviews(user_id);
CREATE INDEX IF NOT EXISTS idx_interviews_status ON interviews(status);
CREATE INDEX IF NOT EXISTS idx_questions_interview_id ON questions(interview_id);

-- Create a recruiter admin account
INSERT INTO users (email, password_hash, role, name)
VALUES ('recruiter@example.com', 
        -- This is a hashed version of 'admin123' - would be generated with werkzeug.security.generate_password_hash in real app
        'pbkdf2:sha256:260000$7tGOBm9yqjJXCvlP$d5e70c2c1ee26ab6d4e82b288bf46ab653a1b08d6b2314a24df7043cd7d2df26', 
        'recruiter', 
        'Admin Recruiter')
ON CONFLICT (email) DO NOTHING;

-- Create sample job roles lookup table
CREATE TABLE IF NOT EXISTS job_roles (
    id SERIAL PRIMARY KEY,
    slug VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL
);

-- Insert common job roles
INSERT INTO job_roles (slug, name) VALUES
    ('sde', 'Software Development Engineer'),
    ('frontend', 'Frontend Developer'),
    ('backend', 'Backend Developer'),
    ('fullstack', 'Full Stack Developer'),
    ('devops', 'DevOps Engineer')
ON CONFLICT (slug) DO NOTHING;

-- Create RLS (Row Level Security) policies
-- Enable RLS on tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE interviews ENABLE ROW LEVEL SECURITY;
ALTER TABLE questions ENABLE ROW LEVEL SECURITY;

-- Create policies
-- Users can only see their own profiles unless they are recruiters
CREATE POLICY users_policy ON users
    USING (id = auth.uid() OR role = 'recruiter');

-- Candidates can only see their own interviews, recruiters can see all
CREATE POLICY interviews_policy ON interviews
    USING ((user_id = (SELECT id FROM users WHERE id = auth.uid())) OR 
           (EXISTS (SELECT 1 FROM users WHERE id = auth.uid() AND role = 'recruiter')));

-- Same for questions
CREATE POLICY questions_policy ON questions
    USING ((interview_id IN (SELECT id FROM interviews WHERE user_id = (SELECT id FROM users WHERE id = auth.uid()))) OR
           (EXISTS (SELECT 1 FROM users WHERE id = auth.uid() AND role = 'recruiter')));

-- Create functions for authentication in Supabase
-- Note: These would typically be created in the Supabase UI or using their CLI tools
-- For a complete setup, you'd also need to configure auth hooks in Supabase

COMMENT ON TABLE users IS 'User accounts for the interview system';
COMMENT ON TABLE interviews IS 'Interview sessions for candidates';
COMMENT ON TABLE questions IS 'Questions asked during interviews';
COMMENT ON TABLE job_roles IS 'Available job roles for interviews';