# Step-by-Step Execution for LocalLift Deployment

This document provides the exact commands and actions to complete the deployment:

## Step 1: Login to Supabase and Apply Database Schema

1. Open your browser and go to: https://rsooolwhapkkkwbmybdb.supabase.co
2. Login with your credentials
3. Navigate to the SQL Editor
4. Create a new query
5. Open this file in VS Code: `C:\Users\PhillMcGurk\Desktop\LocalLift\supabase\migrations\corrected_rbac_schema.sql`
6. Copy the entire content
7. Paste it into the Supabase SQL Editor
8. Click "Run" to execute the query

After running the query, go to the Table Editor and verify that tables like `user_roles` and `customers` have been created.

## Step 2: Login to Railway and Update Environment Variables

1. Open your browser and go to: https://railway.app/project/0e58b112-f5f5-4285-ad1f-f47d1481045b
2. Navigate to your service (humorous-serenity)
3. Click on the "Variables" tab
4. Add the following variables (click "New Variable" for each):

```
Variable Name: POSTGRES_CONNECTION_OPTION
Value: -c AddressFamily=inet
```

```
Variable Name: SUPABASE_DB_HOST
Value: 52.0.91.163
```

```
Variable Name: SUPABASE_DB_PORT
Value: 5432
```

```
Variable Name: SUPABASE_DB_USER
Value: postgres
```

```
Variable Name: SUPABASE_DB_PASSWORD
Value: Sanctuary2025!
```

5. Update the DATABASE_URL to use the IPv4 address:

```
Variable Name: DATABASE_URL
Value: postgresql://postgres:Sanctuary2025!@52.0.91.163:5432/postgres?sslmode=require
```

6. Click "Save Variables"
7. Go to the "Deployments" tab
8. Click "Deploy" to create a new deployment with the updated variables

## Step 3: Create SuperAdmin User in Supabase

1. Go back to Supabase SQL Editor
2. Run this query to get user IDs:

```sql
SELECT id, email FROM auth.users;
```

3. Note down the UUID for your user
4. Run this query to make your user a superadmin (replace the UUID):

```sql
INSERT INTO public.user_roles (user_id, role)
VALUES ('your-user-id-here', 'superadmin');
```

5. Verify admin creation with:

```sql
SELECT * FROM public.user_roles WHERE role = 'superadmin';
```

## Step 4: Verify Deployment

1. Wait for Railway deployment to complete (check logs for connection success)
2. Run the verification script locally:

```
.\verify-deployment.ps1
```

3. Test the frontend by visiting:
```
https://local-lift-adjm0ahjv-admin-cleanexpo247s-projects.vercel.app
```

4. Try logging in with your credentials

## Step 5: Final Checklist

Go through each item in the `COMPLETION_CHECKLIST.md` file and mark as completed.

If any issues persist:
1. Check Railway logs for specific error messages
2. Try updating database connection.py file directly
3. Verify Supabase connection details are correct
4. Check for CORS issues if frontend-backend connection fails
