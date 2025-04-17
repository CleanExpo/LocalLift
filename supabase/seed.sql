-- Seed data for LocalLift application

-- GAMIFICATION DATA

-- Point Types
INSERT INTO gamification.point_types (name, description, multiplier) VALUES
('Review', 'Points earned for submitting business reviews', 1.0),
('Referral', 'Points earned for referring new clients', 2.0),
('Content Creation', 'Points earned for creating marketing content', 1.5),
('Training', 'Points earned for completing training courses', 1.0),
('Performance', 'Points earned for meeting KPIs', 1.0);

-- Additional Achievements
INSERT INTO gamification.achievements (name, description, points, requirements) VALUES
('First Review', 'Submit your first client review', 10, 'Submit 1 review'),
('Review Master', 'Submit 50 client reviews', 100, 'Submit 50 reviews'),
('Referral Champion', 'Refer 10 new clients', 200, 'Make 10 successful referrals'),
('Content Creator', 'Create 5 pieces of marketing content', 75, 'Create 5 content pieces'),
('Training Enthusiast', 'Complete 3 training courses', 150, 'Complete 3 courses'),
('Local SEO Expert', 'Complete all SEO training modules', 300, 'Complete all SEO courses');

-- LEADERBOARDS DATA

-- Leaderboard Types
INSERT INTO leaderboards.leaderboard_types (name, description, scope, timeframe) VALUES
('Global Weekly', 'Weekly leaderboard across all regions and franchises', 'global', 'weekly'),
('Global Monthly', 'Monthly leaderboard across all regions and franchises', 'global', 'monthly'),
('Regional Weekly', 'Weekly leaderboard for each region', 'regional', 'weekly'),
('Regional Monthly', 'Monthly leaderboard for each region', 'regional', 'monthly'),
('Franchise Weekly', 'Weekly leaderboard for each franchise', 'franchise', 'weekly');

-- CERTIFICATIONS DATA

-- Categories
INSERT INTO certifications.categories (name, description) VALUES
('Google My Business', 'GMB optimization and management'),
('Local SEO', 'Local search engine optimization techniques'),
('Review Management', 'Managing and responding to client reviews'),
('Social Media', 'Social media marketing for local businesses'),
('Analytics', 'Data analysis and reporting');

-- Courses
INSERT INTO certifications.courses (category_id, title, description, level, duration_minutes, points_awarded) VALUES
(1, 'GMB Optimization Fundamentals', 'Learn the basics of optimizing Google My Business listings', 1, 120, 50),
(1, 'Advanced GMB Features', 'Master advanced GMB features like posts, Q&A, and messaging', 2, 180, 75),
(2, 'Local SEO Best Practices', 'Core principles of local search optimization', 2, 240, 100),
(3, 'Review Response Strategies', 'How to effectively respond to positive and negative reviews', 1, 90, 50),
(3, 'Review Generation Campaigns', 'Strategies for generating more customer reviews', 2, 120, 75),
(4, 'Social Media for Local Businesses', 'Tailoring social media strategies for local impact', 1, 150, 50),
(5, 'Local Performance Analytics', 'Measuring and analyzing local marketing performance', 3, 210, 125);

-- Modules for GMB Optimization Fundamentals
INSERT INTO certifications.modules (course_id, title, description, sequence_order, duration_minutes) VALUES
(1, 'Introduction to GMB', 'Overview of Google My Business', 1, 15),
(1, 'Setting Up Your GMB Listing', 'Step-by-step guide to creating and claiming a GMB listing', 2, 30),
(1, 'Optimizing Business Information', 'Best practices for business name, address, and categories', 3, 25),
(1, 'Adding Photos and Services', 'How to effectively showcase your business with visual content', 4, 20),
(1, 'Managing Customer Reviews', 'Strategies for handling reviews on your GMB listing', 5, 30);

-- Modules for Advanced GMB Features
INSERT INTO certifications.modules (course_id, title, description, sequence_order, duration_minutes) VALUES
(2, 'GMB Posts and Updates', 'Creating effective posts and updates', 1, 40),
(2, 'Using GMB Messaging', 'Setting up and managing customer messaging', 2, 30),
(2, 'GMB Insights and Analytics', 'Understanding performance metrics', 3, 45),
(2, 'GMB Q&A Management', 'Managing the Q&A section effectively', 4, 35),
(2, 'Advanced Listing Optimization', 'Advanced techniques for GMB ranking', 5, 30);

-- If auth.users table exists and has data, we could add sample user enrollments and progress
