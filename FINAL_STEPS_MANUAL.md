# LocalLift CRM Deployment: Final Manual Steps

This document provides step-by-step instructions to complete the deployment of LocalLift CRM with RBAC functionality.

## Overview

We've successfully accomplished the following:

1. ✅ Created the RBAC schema SQL file
2. ✅ Fixed syntax issues in the schema file (added missing commas)
3. ✅ Built and implemented backend API with proper role checks
4. ✅ Deployed the backend to Railway
5. ✅ Deployed the frontend to Vercel

## Current Status

- **Frontend:** Successfully deployed to Vercel
  - URL: https://local-lift-adjm0ahjv-admin-cleanexpo247s-projects.vercel.app

- **Backend:** Deployed to Railway but has a database connection issue
  - URL: https://locallift-production.up.railway.app
  - Issue: IPv6 connectivity problem to Supabase

## Manual Steps to Complete Deployment

### Step 1: Fix Railway Database Connection

1. Follow the detailed instructions in `MANUAL_RAILWAY_SUPABASE_FIX.md`
   - Log in to Railway dashboard
   - Navigate to your project settings
   - Update environment variables to force IPv4 connection

### Step 2: Apply Supabase Database Migration

1. Log in to Supabase dashboard: https://rsooolwhapkkkwbmybdb.supabase.co
2. Navigate to SQL Editor
3. Open the **fixed** SQL file: `supabase/migrations/20250419_rbac_schema_fixed.sql`
4. Copy the entire content
5. Paste into the Supabase SQL Editor
6. Execute the SQL

The RBAC schema has been fixed with proper commas in the SQL file. The original file was missing commas in several places.

### Step 3: Create SuperAdmin User

After completing steps 1 and 2:

1. Visit the frontend site: https://local-lift-adjm0ahjv-admin-cleanexpo247s-projects.vercel.app/login/
2. Register a new user account
3. Go to Supabase dashboard
4. Navigate to Authentication → Users
5. Find your newly registered user (look for your email)
6. Copy the user ID
7. Execute this SQL in the Supabase SQL Editor:
   ```sql
   INSERT INTO public.user_roles (user_id, role) 
   VALUES ('YOUR-USER-ID', 'superadmin');
   ```
   (Replace 'YOUR-USER-ID' with the actual user ID you copied)

### Step 4: Verify Complete System

1. Log in with your superadmin account
2. Verify you can access all areas of the dashboard
3. Test creating another user with a different role
4. Check that RBAC controls access properly based on role

## Troubleshooting

### Database Connection Issues

If you're still experiencing database connection issues after following the instructions in `MANUAL_RAILWAY_SUPABASE_FIX.md`:

1. Check Supabase connection pooling:
   - In Supabase dashboard, go to Project Settings → Database → Connection Pooling
   - Enable connection pooling
   - Update the DATABASE_URL in Railway with the provided pooling URL

2. Check for IPv6 related issues:
   - Railway may be attempting to connect to Supabase using IPv6
   - The `POSTGRES_CONNECTION_OPTION="-c AddressFamily=inet"` environment variable forces IPv4 connections

### JWT Authentication Issues

If users can't log in with proper roles:

1. Check that the JWT trigger was properly created:
   ```sql
   DROP TRIGGER IF EXISTS add_role_to_jwt ON auth.tokens;
   CREATE TRIGGER add_role_to_jwt
     BEFORE INSERT ON auth.tokens
     FOR EACH ROW
     EXECUTE PROCEDURE public.add_role_to_jwt();
   ```

2. Verify user roles are set correctly in Supabase:
   ```sql
   SELECT * FROM public.user_roles;
   ```

## Next Development Steps

After successful deployment:

1. Create additional user roles (staff, manager, etc.)
2. Add sample data to test CRM functionality
3. Create end-user documentation
4. Set up monitoring and logging
5. Implement backup strategy

## Support Resources

- Supabase Documentation: https://supabase.com/docs
- Railway Documentation: https://docs.railway.app
- FastAPI Documentation: https://fastapi.tiangolo.com
- Vercel Documentation: https://vercel.com/docs
