# Manual Supabase Migration Instructions

Since the automated migration script encountered a 404 error, we'll need to apply the SQL migration manually through the Supabase dashboard.

## Steps to Apply the Migration:

1. Log in to the Supabase dashboard at https://rsooolwhapkkkwbmybdb.supabase.co
2. Navigate to the SQL Editor
3. Create a new query
4. Copy and paste the entire SQL content from the `supabase/migrations/20250419_rbac_schema_fixed.sql` file
5. Execute the query

## Creating a SuperAdmin User:

After the migration completes successfully, you'll need to create a SuperAdmin user. To do this:

1. Return to the SQL Editor in the Supabase dashboard
2. Create a new query
3. First, identify your user ID by running:
   ```sql
   SELECT id, email FROM auth.users;
   ```
4. Then create a SuperAdmin role for your user by running (replace YOUR_USER_ID with your actual user ID):
   ```sql
   INSERT INTO public.user_roles (user_id, role)
   VALUES ('YOUR_USER_ID', 'superadmin');
   ```

## Verifying the Migration:

To verify that the migration was applied correctly:

1. Go to the Table Editor in Supabase
2. Confirm that the following tables exist:
   - user_roles
   - user_teams
   - user_profiles
   - customers
   - temp_permissions
   - role_change_logs
   - activity_logs
   - access_logs
   - user_preferences
   - customer_interactions
   - customer_reviews
   - customer_inquiries
   - website_visits
   - customer_engagement
   - orders
   - reports

## Note on IPv6/IPv4 Connection Issue:

We've fixed the IPv6/IPv4 connection issue in Railway by:
1. Updating the DATABASE_URL to use the IPv4 address instead of the hostname
2. Setting the POSTGRES_CONNECTION_OPTION to force IPv4 connections
3. Deploying the updated settings to Railway

You may need to:
1. Verify that the Railway deployment completed successfully
2. Check the Railway logs to confirm that the database connection is now working
3. Run the verify-deployment.ps1 script to test the overall system
