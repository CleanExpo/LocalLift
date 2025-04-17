-- Achievement System Migration
-- This file creates the schema for tracking achievements in the badge system
-- Achievements include milestones and streaks that clients can earn

-- Create achievement log table to track client achievements
CREATE TABLE IF NOT EXISTS achievement_log (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id uuid REFERENCES auth.users(id),
  type text NOT NULL, -- e.g. 'milestone', 'streak'
  label text NOT NULL, -- e.g. '5 Badges Earned'
  earned_at timestamptz DEFAULT now(),
  metadata jsonb
);

-- Add indexes for faster lookups
CREATE INDEX IF NOT EXISTS idx_achievement_log_client_id ON achievement_log(client_id);
CREATE INDEX IF NOT EXISTS idx_achievement_log_type ON achievement_log(type);

-- Enable RLS (Row Level Security)
ALTER TABLE achievement_log ENABLE ROW LEVEL SECURITY;

-- Create policy for admin access
CREATE POLICY admin_achievement_log ON achievement_log
  FOR ALL USING (
    (auth.uid() IN (SELECT id FROM admin_users))
  );

-- Create policy for client to view their own achievements
CREATE POLICY read_own_achievements ON achievement_log
  FOR SELECT USING (
    client_id = auth.uid()
  );

-- Create function to get streak count for a client
CREATE OR REPLACE FUNCTION get_streak_count(client_id uuid)
RETURNS int
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  streak_count int;
BEGIN
  -- Count consecutive weeks with badges earned, starting from the most recent
  WITH streak_weeks AS (
    SELECT
      week_id,
      ROW_NUMBER() OVER (ORDER BY week_id DESC) AS row_num
    FROM badge_history
    WHERE client_id = $1
      AND earned = true
    ORDER BY week_id DESC
  )
  SELECT
    COUNT(*)
  INTO
    streak_count
  FROM streak_weeks
  WHERE row_num = (
    SELECT row_number() OVER (ORDER BY week_id DESC)
    FROM badge_history
    WHERE client_id = $1
      AND earned = true
    ORDER BY week_id DESC
    LIMIT 1
  );
  
  RETURN streak_count;
END;
$$;

-- Create function to check and record achievements
CREATE OR REPLACE FUNCTION check_achievements(client_id uuid)
RETURNS json
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  earned_count int;
  streak_count int;
  new_achievements json;
BEGIN
  -- Get total badge count
  SELECT COUNT(*)
  INTO earned_count
  FROM badge_history
  WHERE client_id = $1
    AND earned = true;
  
  -- Check badge count milestones
  IF earned_count = 5 THEN
    INSERT INTO achievement_log (client_id, type, label, metadata)
    VALUES ($1, 'milestone', 'Bronze Badge Earned', jsonb_build_object('badges_earned', earned_count))
    ON CONFLICT DO NOTHING;
  ELSIF earned_count = 10 THEN
    INSERT INTO achievement_log (client_id, type, label, metadata)
    VALUES ($1, 'milestone', 'Silver Badge Earned', jsonb_build_object('badges_earned', earned_count))
    ON CONFLICT DO NOTHING;
  ELSIF earned_count = 20 THEN
    INSERT INTO achievement_log (client_id, type, label, metadata)
    VALUES ($1, 'milestone', 'Gold Badge Earned', jsonb_build_object('badges_earned', earned_count))
    ON CONFLICT DO NOTHING;
  END IF;
  
  -- Check streak achievements
  streak_count := get_streak_count($1);
  
  IF streak_count = 3 THEN
    INSERT INTO achievement_log (client_id, type, label, metadata)
    VALUES ($1, 'streak', '3-Week Streak Unlocked!', jsonb_build_object('streak_length', streak_count))
    ON CONFLICT DO NOTHING;
  ELSIF streak_count = 5 THEN
    INSERT INTO achievement_log (client_id, type, label, metadata)
    VALUES ($1, 'streak', '5-Week Streak Unlocked!', jsonb_build_object('streak_length', streak_count))
    ON CONFLICT DO NOTHING;
  ELSIF streak_count = 10 THEN
    INSERT INTO achievement_log (client_id, type, label, metadata)
    VALUES ($1, 'streak', '10-Week Streak Unlocked!', jsonb_build_object('streak_length', streak_count))
    ON CONFLICT DO NOTHING;
  END IF;
  
  -- Return newly earned achievements
  SELECT jsonb_agg(a.*)::json
  INTO new_achievements
  FROM achievement_log a
  WHERE a.client_id = $1
    AND a.earned_at > (now() - interval '1 minute');
  
  RETURN new_achievements;
END;
$$;

-- Create a trigger to automatically check achievements when a badge is earned
CREATE OR REPLACE FUNCTION trigger_check_achievements()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
  -- If a badge was earned, check for achievements
  IF NEW.earned = true THEN
    PERFORM check_achievements(NEW.client_id);
  END IF;
  
  RETURN NEW;
END;
$$;

-- Attach the trigger to the badge_history table
DROP TRIGGER IF EXISTS badge_earned_achievement_check ON badge_history;
CREATE TRIGGER badge_earned_achievement_check
AFTER INSERT OR UPDATE ON badge_history
FOR EACH ROW
EXECUTE FUNCTION trigger_check_achievements();

-- Add comments for documentation
COMMENT ON TABLE achievement_log IS 'Tracks achievements earned by clients';
COMMENT ON FUNCTION get_streak_count IS 'Calculates the current streak count for a client';
COMMENT ON FUNCTION check_achievements IS 'Checks and records new achievements for a client';
COMMENT ON FUNCTION trigger_check_achievements IS 'Automatically checks for achievements when badges are earned';
