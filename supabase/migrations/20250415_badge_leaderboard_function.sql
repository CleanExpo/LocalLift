-- Add a SQL function for calculating the badge leaderboard
-- This function allows for efficient leaderboard calculation in the database
-- rather than in application code, improving performance for large datasets

-- Create the badge leaderboard function
CREATE OR REPLACE FUNCTION get_badge_leaderboard(
    timeframe TEXT DEFAULT 'all',
    limit_count INTEGER DEFAULT 10
)
RETURNS TABLE (
    rank INTEGER,
    client_id UUID,
    client_name TEXT,
    region TEXT,
    badges_earned INTEGER,
    compliance_rate NUMERIC,
    total_weeks INTEGER,
    total_compliant_posts INTEGER,
    total_posts INTEGER,
    average_posts NUMERIC,
    current_streak INTEGER
) LANGUAGE plpgsql
SECURITY DEFINER -- Run with privileges of the function creator
AS $$
DECLARE
    start_week_id TEXT;
BEGIN
    -- Set the start week based on timeframe
    CASE timeframe
        WHEN 'week' THEN 
            -- Current week
            start_week_id := to_char(now(), 'IYYY-"W"IW');
        WHEN 'month' THEN
            -- First week of current month
            start_week_id := to_char(date_trunc('month', now()), 'IYYY-"W"IW');
        WHEN 'quarter' THEN
            -- First week of current quarter
            start_week_id := to_char(date_trunc('quarter', now()), 'IYYY-"W"IW');
        WHEN 'year' THEN
            -- First week of current year
            start_week_id := to_char(date_trunc('year', now()), 'IYYY-"W"IW');
        ELSE
            -- All time - no start week filter
            start_week_id := NULL;
    END CASE;

    RETURN QUERY
    WITH client_stats AS (
        SELECT
            bh.client_id,
            c.name AS client_name,
            c.region,
            COUNT(*) AS total_weeks,
            SUM(CASE WHEN bh.earned THEN 1 ELSE 0 END) AS badges_earned,
            SUM(bh.compliant) AS total_compliant_posts,
            SUM(bh.total) AS total_posts,
            -- Calculate current streak using window functions
            MAX(
                SUM(CASE WHEN bh.earned THEN 1 ELSE 0 END) 
                OVER (PARTITION BY bh.client_id ORDER BY bh.week_id ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
            ) AS current_streak
        FROM
            badge_history bh
            JOIN clients c ON bh.client_id = c.id
        WHERE
            (start_week_id IS NULL OR bh.week_id >= start_week_id)
        GROUP BY
            bh.client_id, c.name, c.region
    )
    SELECT
        ROW_NUMBER() OVER (ORDER BY cs.badges_earned DESC, 
                         (cs.badges_earned::NUMERIC / NULLIF(cs.total_weeks, 0) * 100) DESC) AS rank,
        cs.client_id,
        cs.client_name,
        cs.region,
        cs.badges_earned,
        ROUND((cs.badges_earned::NUMERIC / NULLIF(cs.total_weeks, 0) * 100), 1) AS compliance_rate,
        cs.total_weeks,
        cs.total_compliant_posts,
        cs.total_posts,
        ROUND((cs.total_posts::NUMERIC / NULLIF(cs.total_weeks, 0)), 1) AS average_posts,
        cs.current_streak
    FROM
        client_stats cs
    ORDER BY
        rank ASC
    LIMIT limit_count;
END;
$$;

-- Add comment for documentation
COMMENT ON FUNCTION get_badge_leaderboard IS 'Returns a leaderboard of clients ranked by badge earning performance for the specified timeframe';
