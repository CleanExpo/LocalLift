-- Create simplified badge leaderboard function
-- This function focuses solely on counting the total number of badges earned by each client
-- It's a simpler alternative to the more comprehensive get_badge_leaderboard function

create or replace function get_simple_badge_leaderboard()
returns table (
  client_id uuid,
  client_name text,
  badge_count integer,
  rank integer
)
language sql
as $$
  select 
    bh.client_id,
    c.name as client_name,
    count(*) as badge_count,
    row_number() over (order by count(*) desc) as rank
  from badge_history bh
  join clients c on bh.client_id = c.id
  where bh.earned = true
  group by bh.client_id, c.name
  order by badge_count desc;
$$;

-- Add comment for documentation
COMMENT ON FUNCTION get_simple_badge_leaderboard IS 'Returns a simple leaderboard of clients ranked by total number of badges earned';

-- Create time-limited version of the simplified leaderboard function
create or replace function get_simple_badge_leaderboard_time_limited(
  timeframe text default 'all'
)
returns table (
  client_id uuid,
  client_name text,
  badge_count integer,
  rank integer
)
language plpgsql
as $$
declare
  start_week_id text;
begin
  -- Set the start week based on timeframe
  case timeframe
    when 'week' then 
      -- Current week
      start_week_id := to_char(now(), 'IYYY-"W"IW');
    when 'month' then
      -- First week of current month
      start_week_id := to_char(date_trunc('month', now()), 'IYYY-"W"IW');
    when 'quarter' then
      -- First week of current quarter
      start_week_id := to_char(date_trunc('quarter', now()), 'IYYY-"W"IW');
    when 'year' then
      -- First week of current year
      start_week_id := to_char(date_trunc('year', now()), 'IYYY-"W"IW');
    else
      -- All time - no start week filter
      start_week_id := null;
  end case;

  return query
  select 
    bh.client_id,
    c.name as client_name,
    count(*) as badge_count,
    row_number() over (order by count(*) desc) as rank
  from badge_history bh
  join clients c on bh.client_id = c.id
  where 
    bh.earned = true and
    (start_week_id is null or bh.week_id >= start_week_id)
  group by bh.client_id, c.name
  order by badge_count desc;
end;
$$;

-- Add comment for documentation
COMMENT ON FUNCTION get_simple_badge_leaderboard_time_limited IS 'Returns a simple leaderboard of clients ranked by badges earned within the specified timeframe';
