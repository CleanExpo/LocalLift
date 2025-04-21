# LocalLift CRM: Final Deployment Manual Steps

Since automatic script deployment has encountered various issues, here's a step-by-step manual process to complete the deployment:

## 1. Manual Railway Environment Variable Setup

Log into the Railway dashboard and set these critical environment variables:

1. Go to: https://railway.app/project/0e58b112-f5f5-4285-ad1f-f47d1481045b
2. Navigate to your service (humorous-serenity)
3. Click on the "Variables" tab
4. Add or update the following variables:
   ```
   POSTGRES_CONNECTION_OPTION=-c AddressFamily=inet
   SUPABASE_DB_HOST=52.0.91.163
   SUPABASE_DB_PORT=5432
   SUPABASE_DB_USER=postgres
   SUPABASE_DB_PASSWORD=postgres_password
   DATABASE_URL=postgresql://postgres:postgres_password@52.0.91.163:5432/postgres?sslmode=require
   ```
5. Click "Save" and allow Railway to redeploy automatically

## 2. Manual Supabase Database Schema Migration

Since the script encountered a 404 error, you'll need to apply the schema manually:

1. Log in to the Supabase dashboard at https://rsooolwhapkkkwbmybdb.supabase.co
2. Navigate to the SQL Editor section
3. Create a new query
4. Open the file `supabase/migrations/20250419_rbac_schema_fixed.sql` locally
5. Copy and paste the entire SQL content into the query editor
6. Execute the query to create all tables, functions, and policies

## 3. Create a SuperAdmin User

After the migration is complete, create your admin account:

1. Go back to the SQL Editor in Supabase
2. Create a new query
3. Run this query to view existing users:
   ```sql
   SELECT id, email FROM auth.users;
   ```
4. Note your user ID, then run this query (replace YOUR_USER_ID with your actual ID):
   ```sql
   INSERT INTO public.user_roles (user_id, role)
   VALUES ('YOUR_USER_ID', 'superadmin');
   ```

## 4. Update the Database Connection in Railway

If the IPv4 connection is still failing after setting environment variables:

1. Go back to Railway dashboard
2. Click on the "Deployments" tab
3. Click "Deploy" to create a new deployment with the updated variables
4. When deployment completes, check the logs to verify if the connection is successful

## 5. Verify the Frontend-Backend Connection

1. Visit the Vercel-hosted frontend at: https://local-lift-adjm0ahjv-admin-cleanexpo247s-projects.vercel.app
2. Attempt to log in with your credentials
3. If login fails, check if the frontend is properly calling the backend API
4. Verify the API endpoint URLs in the frontend code match the Railway deployment URL

## 6. Test the Deployment with Health Check

After all steps are complete, test the deployment:

1. Run the verification script locally:
   ```
   .\verify-deployment.ps1
   ```
2. Alternatively, try accessing the health endpoint directly:
   https://locallift-production.up.railway.app/health

## 7. Final Production Checklist

- [  ] Backend deployed successfully to Railway
- [  ] Frontend deployed successfully to Vercel
- [  ] Database schema migrated to Supabase
- [  ] SuperAdmin user created
- [  ] Database connection using IPv4 works
- [  ] Authentication works
- [  ] Frontend can communicate with backend
- [  ] Basic functionality can be tested

If you encounter persistent issues, you may need to:
1. Check your actual Supabase database password (if different from "postgres_password")
2. Verify the IP address for Supabase (currently using 52.0.91.163)
3. Test the connection from Railway to Supabase with a simple diagnostic endpoint
