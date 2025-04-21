# LocalLift CRM: Final Execution Steps

This document provides the exact sequence of execution steps to complete the LocalLift CRM deployment, building on the documentation we've created so far.

## Step 1: Apply the Database Schema to Supabase

1. **Login to Supabase Dashboard**
   - Go to https://rsooolwhapkkkwbmybdb.supabase.co
   - Login with your credentials

2. **Apply the Corrected Schema**
   - Navigate to the SQL Editor section
   - Create a new query
   - Open the corrected SQL file locally: `C:\Users\PhillMcGurk\Desktop\LocalLift\supabase\migrations\corrected_rbac_schema.sql`
   - Copy the entire contents and paste into the SQL Editor
   - Click "Run" to execute the query
   - This might take a few minutes to complete

3. **Verify Schema Creation**
   - Go to the Table Editor
   - Confirm that tables like `user_roles`, `user_teams`, `customers`, etc. have been created
   - If any errors occurred, check the SQL Editor output for specific issues

## Step 2: Set Environment Variables in Railway

1. **Login to Railway Dashboard**
   - Go to https://railway.app/project/0e58b112-f5f5-4285-ad1f-f47d1481045b
   
2. **Configure IPv4 Connection Variables**
   - Navigate to your service (humorous-serenity)
   - Click on the "Variables" tab
   - Add or update the following variables:
     ```
     POSTGRES_CONNECTION_OPTION=-c AddressFamily=inet
     SUPABASE_DB_HOST=52.0.91.163
     SUPABASE_DB_PORT=5432
     SUPABASE_DB_USER=postgres
     SUPABASE_DB_PASSWORD=postgres_password
     DATABASE_URL=postgresql://postgres:postgres_password@52.0.91.163:5432/postgres?sslmode=require
     ```
   - Make sure the other essential variables are already set:
     ```
     SUPABASE_URL=https://rsooolwhapkkkwbmybdb.supabase.co
     SUPABASE_SERVICE_ROLE_KEY=[your-service-role-key]
     FRONTEND_URL=https://local-lift-fxu1otnh4-admin-cleanexpo247s-projects.vercel.app
     JWT_SECRET=superSecretJWTKeyForLocalLiftRBAC2025
     ```
   - Click "Save Variables"

3. **Trigger a Redeployment**
   - Go to the "Deployments" tab
   - Click "Deploy" to create a new deployment with the updated variables
   - Wait for the deployment to complete

## Step 3: Create SuperAdmin User

1. **Identify User ID**
   - Go back to Supabase SQL Editor
   - Run the following query to get the user IDs:
     ```sql
     SELECT id, email FROM auth.users;
     ```
   - Note down the UUID for the user you want to make a superadmin

2. **Create SuperAdmin Role**
   - In the same SQL Editor, run:
     ```sql
     INSERT INTO public.user_roles (user_id, role)
     VALUES ('your-user-id-here', 'superadmin');
     ```
   - Replace 'your-user-id-here' with the actual UUID you noted
   
3. **Verify Admin Creation**
   - Run this query to confirm:
     ```sql
     SELECT * FROM public.user_roles WHERE role = 'superadmin';
     ```

## Step 4: Verify the Deployment

1. **Check Railway Connection**
   - Monitor the deployment logs in Railway
   - Look for any connection errors
   - The log should show "Database engine created and connection successful" without IPv6 errors

2. **Test API Endpoints**
   - Open a browser and navigate to:
     ```
     https://locallift-production.up.railway.app/health
     ```
   - You should get a successful response, not a 404 error

3. **Verify Frontend Integration**
   - Open the Vercel-deployed frontend:
     ```
     https://local-lift-adjm0ahjv-admin-cleanexpo247s-projects.vercel.app
     ```
   - Try to log in with your credentials
   - Verify you can access admin features

## Step 5: Final Verification

1. **Run Local Verification Script**
   - Execute:
     ```
     .\verify-deployment.ps1
     ```
   - Review the output for any issues

2. **Complete the Checklist**
   - Go through each item in the `COMPLETION_CHECKLIST.md` file
   - Mark each item as completed once verified

## Troubleshooting Common Issues

### Railway Connection Issues
- If still encountering IPv6/IPv4 issues, try updating `core/database/connection.py` to hardcode the IPv4 address
- Try a different IPv4 address if 52.0.91.163 doesn't work
- Check if your Supabase password is different from the default

### Supabase Migration Errors
- If encountering SQL errors, run each CREATE TABLE statement individually
- Check for syntax errors in function definitions
- Ensure the uuid-ossp extension is properly installed

### Authentication Issues
- Verify JWT_SECRET is correctly set in Railway
- Check CORS settings in backend for frontend access
- Ensure Supabase URL and key are correct

## Next Steps After Deployment

1. **Security Hardening**
   - Review security settings
   - Configure backups
   - Set up monitoring

2. **User Training**
   - Provide access to documentation
   - Schedule training sessions
   - Set up support channels

3. **Performance Monitoring**
   - Set up logging
   - Configure alerts
   - Establish a maintenance schedule
