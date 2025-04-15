-- Create admin badge leaderboard function for dashboard
-- This function returns comprehensive badge information for the admin dashboard
-- including badge counts, streaks, and last badge earned dates

create or replace function get_admin_badge_leaderboard()
returns table (
  client_id uuid,
  client_email text,
  client_name text,
  region text,
  badge_count int,
  streak int,
  last_earned timestamp with time zone
)
language sql
security definer
as $$
  with badge_stats as (
    -- Get badge count per client
    select
      c.id as client_id,
      c.email as client_email,
      c.name as client_name,
      c.region,
      count(case when bh.earned = true then 1 end) as badge_count,
      -- Get current streak
      (
        select count(*)
        from (
          select
            row_number() over (order by week_id desc) as row_num,
            week_id
          from badge_history
          where client_id = c.id
            and earned = true
          order by week_id desc
        ) as recent_badges
        where recent_badges.row_num = (
          select row_number() over (order by week_id desc)
          from badge_history
          where client_id = c.id
            and earned = true
          order by week_id desc
          limit 1
        )
      ) as streak,
      -- Get last badge earned date
      max(case when bh.earned = true then bh.created_at end) as last_earned
    from
      clients c
    left join
      badge_history bh on c.id = bh.client_id
    group by
      c.id, c.email, c.name, c.region
  )
  
  select
    client_id,
    client_email,
    client_name,
    region,
    badge_count,
    streak,
    last_earned
  from
    badge_stats
  order by
    badge_count desc,
    last_earned desc nulls last;
$$;

-- Create badge statistics function for admin dashboard
create or replace function get_badge_statistics()
returns json
language plpgsql
security definer
as $$
declare
  total_badges int;
  active_clients int;
  total_clients int;
  total_posts int;
  compliant_posts int;
  compliance_rate numeric;
  current_week_id text;
  current_week_badges int;
  current_week_clients int;
  current_week_completion numeric;
begin
  -- Get current ISO week
  current_week_id := to_char(now(), 'IYYY-"W"IW');
  
  -- Calculate global statistics
  select
    count(case when bh.earned = true then 1 end),
    count(distinct case when bh.earned = true then bh.client_id end),
    count(distinct c.id),
    sum(bh.total),
    sum(bh.compliant)
  into
    total_badges,
    active_clients,
    total_clients,
    total_posts,
    compliant_posts
  from
    badge_history bh
  right join
    clients c on bh.client_id = c.id;
  
  -- Calculate compliance rate
  compliance_rate := case when total_posts > 0 then round((compliant_posts::numeric / total_posts::numeric) * 100, 1) else 0 end;
  
  -- Calculate current week statistics
  select
    count(case when bh.earned = true then 1 end),
    count(distinct bh.client_id)
  into
    current_week_badges,
    current_week_clients
  from
    badge_history bh
  where
    bh.week_id = current_week_id;
  
  -- Calculate current week completion rate
  current_week_completion := case when current_week_clients > 0 then round((current_week_badges::numeric / current_week_clients::numeric) * 100, 1) else 0 end;
  
  -- Return as JSON
  return json_build_object(
    'total_badges_earned', total_badges,
    'active_clients', active_clients,
    'total_clients', total_clients,
    'total_posts', total_posts,
    'compliant_posts', compliant_posts,
    'compliance_rate', compliance_rate,
    'current_week_id', current_week_id,
    'current_week_badges', current_week_badges, 
    'current_week_clients', current_week_clients,
    'current_week_completion', current_week_completion
  );
end;
$$;

-- Create regional badge performance function for admin dashboard
create or replace function get_regional_badge_stats()
returns table (
  region text,
  total_clients int,
  active_clients int,
  participation_rate numeric,
  total_badges int,
  avg_badges_per_client numeric
)
language sql
security definer
as $$
  with region_stats as (
    select
      c.region,
      count(distinct c.id) as total_clients,
      count(distinct case when bh.earned = true then c.id end) as active_clients,
      count(case when bh.earned = true then 1 end) as total_badges
    from
      clients c
    left join
      badge_history bh on c.id = bh.client_id
    group by
      c.region
  )
  
  select
    coalesce(region, 'Unknown') as region,
    total_clients,
    active_clients,
    case when total_clients > 0 then round((active_clients::numeric / total_clients::numeric) * 100, 1) else 0 end as participation_rate,
    total_badges,
    case when total_clients > 0 then round((total_badges::numeric / total_clients::numeric), 2) else 0 end as avg_badges_per_client
  from
    region_stats
  order by
    total_badges desc;
$$;

-- Add comments for documentation
COMMENT ON FUNCTION get_admin_badge_leaderboard IS 'Returns badge leaderboard data for admin dashboard';
COMMENT ON FUNCTION get_badge_statistics IS 'Returns global badge statistics for admin dashboard';
COMMENT ON FUNCTION get_regional_badge_stats IS 'Returns badge statistics grouped by region for admin dashboard';
