-- Migration to add badge tracking history table
-- This table stores the history of client badge status over time
-- Used for analytics, progress tracking, and historical reporting

-- Create badge_history table
CREATE TABLE IF NOT EXISTS badge_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    week_id VARCHAR(10) NOT NULL, -- Format: YYYY-WXX (e.g., 2025-W15)
    earned BOOLEAN NOT NULL DEFAULT FALSE,
    compliant INTEGER NOT NULL DEFAULT 0,
    total INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraint to ensure unique records per client per week
    CONSTRAINT unique_client_week UNIQUE (client_id, week_id)
);

-- Create index for faster lookups by client
CREATE INDEX IF NOT EXISTS idx_badge_history_client_id ON badge_history(client_id);

-- Create index for faster lookups by week
CREATE INDEX IF NOT EXISTS idx_badge_history_week_id ON badge_history(week_id);

-- Add RLS policies
ALTER TABLE badge_history ENABLE ROW LEVEL SECURITY;

-- Policy for administrators - full access
CREATE POLICY admin_all_access 
ON badge_history 
FOR ALL 
TO authenticated 
USING (
    EXISTS (
        SELECT 1 FROM user_roles 
        WHERE user_roles.user_id = auth.uid() 
        AND user_roles.role = 'admin'
    )
);

-- Policy for clients - read only their own data
CREATE POLICY client_view_own 
ON badge_history 
FOR SELECT 
TO authenticated 
USING (
    client_id IN (
        SELECT client_id FROM client_users
        WHERE client_users.user_id = auth.uid()
    )
);

-- Create trigger to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_badge_history_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_badge_history_timestamp
BEFORE UPDATE ON badge_history
FOR EACH ROW
EXECUTE FUNCTION update_badge_history_updated_at();

-- Add badge_history tracking to realtime publication (if realtime is used)
ALTER PUBLICATION supabase_realtime ADD TABLE badge_history;

-- Add comments for documentation
COMMENT ON TABLE badge_history IS 'Historical record of client badge status by week';
COMMENT ON COLUMN badge_history.week_id IS 'ISO week identifier in YYYY-WXX format';
COMMENT ON COLUMN badge_history.earned IS 'Whether the client earned a badge for this week';
COMMENT ON COLUMN badge_history.compliant IS 'Number of compliant posts for the week';
COMMENT ON COLUMN badge_history.total IS 'Total number of posts for the week';
