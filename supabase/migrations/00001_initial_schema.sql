-- Migration 00001: Initial Schema Setup for LocalLift

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create schemas
CREATE SCHEMA IF NOT EXISTS gamification;
CREATE SCHEMA IF NOT EXISTS leaderboards;
CREATE SCHEMA IF NOT EXISTS certifications;

-- GAMIFICATION SCHEMA

-- Points Types
CREATE TABLE gamification.point_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    multiplier DECIMAL(5,2) DEFAULT 1.0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Levels
CREATE TABLE gamification.levels (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    min_points INTEGER NOT NULL,
    max_points INTEGER NOT NULL,
    icon_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT min_less_than_max CHECK (min_points < max_points)
);

-- Achievements
CREATE TABLE gamification.achievements (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    points INTEGER DEFAULT 0,
    badge_url TEXT,
    requirements TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- User Points (references auth.users table created by Supabase)
CREATE TABLE gamification.user_points (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    point_type_id INTEGER REFERENCES gamification.point_types(id),
    amount INTEGER NOT NULL DEFAULT 0,
    description TEXT,
    awarded_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- User Achievements
CREATE TABLE gamification.user_achievements (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    achievement_id INTEGER NOT NULL REFERENCES gamification.achievements(id),
    awarded_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, achievement_id)
);

-- LEADERBOARDS SCHEMA

-- Leaderboard Types
CREATE TABLE leaderboards.leaderboard_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    scope VARCHAR(50) NOT NULL, -- 'global', 'regional', 'franchise'
    timeframe VARCHAR(50), -- 'daily', 'weekly', 'monthly', 'all-time', etc.
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Leaderboard Entries
CREATE TABLE leaderboards.entries (
    id SERIAL PRIMARY KEY,
    leaderboard_type_id INTEGER NOT NULL REFERENCES leaderboards.leaderboard_types(id),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    score INTEGER NOT NULL DEFAULT 0,
    rank INTEGER,
    region_id INTEGER, -- References to a regions table (if needed)
    franchise_id INTEGER, -- References to a franchises table (if needed)
    period_start TIMESTAMPTZ,
    period_end TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- CERTIFICATIONS SCHEMA

-- Course Categories
CREATE TABLE certifications.categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    icon_url TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Courses
CREATE TABLE certifications.courses (
    id SERIAL PRIMARY KEY,
    category_id INTEGER REFERENCES certifications.categories(id),
    title VARCHAR(200) NOT NULL,
    description TEXT,
    level INTEGER DEFAULT 1, -- 1=Beginner, 2=Intermediate, 3=Advanced
    duration_minutes INTEGER,
    points_awarded INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Course Modules
CREATE TABLE certifications.modules (
    id SERIAL PRIMARY KEY,
    course_id INTEGER NOT NULL REFERENCES certifications.courses(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    content_url TEXT,
    sequence_order INTEGER NOT NULL,
    duration_minutes INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- User Course Enrollments
CREATE TABLE certifications.enrollments (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    course_id INTEGER NOT NULL REFERENCES certifications.courses(id),
    enrolled_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    progress_percentage DECIMAL(5,2) DEFAULT 0,
    is_certified BOOLEAN DEFAULT FALSE,
    certification_issued_at TIMESTAMPTZ,
    certification_expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, course_id)
);

-- User Module Progress
CREATE TABLE certifications.module_progress (
    id SERIAL PRIMARY KEY,
    enrollment_id INTEGER NOT NULL REFERENCES certifications.enrollments(id) ON DELETE CASCADE,
    module_id INTEGER NOT NULL REFERENCES certifications.modules(id),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    is_complete BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(enrollment_id, module_id)
);

-- Initial sample data
INSERT INTO gamification.levels (name, description, min_points, max_points) VALUES
('Rookie', 'Just starting out', 0, 99),
('Novice', 'Learning the ropes', 100, 249),
('Expert', 'Mastering the skills', 250, 499);

-- Add RLS policies later if needed
