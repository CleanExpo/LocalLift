# Manual Railway-Supabase Connection Fix

This guide provides manual steps to fix the connection between your Railway deployment and Supabase database.

## Problem Identified

The Railway deployment logs show a connection issue:

```
DATABASE ENGINE CREATION FAILED: Connection to server at "db.rsooolwhapkkkwbmybdb.supabase.co" failed: Network is unreachable
```

This appears to be an IPv6 connectivity issue, where Railway is trying to connect to Supabase via IPv6 but can't reach it.

## Manual Fix Steps

1. **Log in to Railway Dashboard**
   - Go to [Railway Dashboard](https://railway.app/dashboard)
   - Sign in with your credentials

2. **Navigate to Your Project**
   - Select the "LocalLift" project
   - Select your service (usually with the same name as your project)

3. **Update Environment Variables**
   - Click on the "Variables" tab
   - Add/Update the following variables:

   ```
   SUPABASE_URL=https://rsooolwhapkkkwbmybdb.supabase.co
   SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJzb29vbHdoYXBra2t3Ym15YmRiIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NDcwODU0NiwiZXhwIjoyMDYwMjg0NTQ2fQ.4z9OqyeU9-CHmDtZwA87ymicFEM-U53yzdeTZwc6KdE
   FRONTEND_URL=https://local-lift-adjm0ahjv-admin-cleanexpo247s-projects.vercel.app
   JWT_SECRET=superSecretJWTKeyForLocalLiftRBAC2025
   ```

4. **Force IPv4 Connection**
   - Add these additional variables to force IPv4 connection:

   ```
   SUPABASE_DB_HOST=db.rsooolwhapkkkwbmybdb.supabase.co
   SUPABASE_DB_PORT=5432
   SUPABASE_DB_USER=postgres
   SUPABASE_DB_PASSWORD=your-postgres-password
   DATABASE_URL=postgresql://postgres:your-postgres-password@db.rsooolwhapkkkwbmybdb.supabase.co:5432/postgres?sslmode=require
   POSTGRES_CONNECTION_OPTION="-c AddressFamily=inet"
   ```

   Replace `your-postgres-password` with your actual Supabase PostgreSQL password.

5. **Restart Your Service**
   - After adding all variables, click on the "Deployments" tab
   - Find your latest deployment
   - Click the "Redeploy" button to deploy with new variables

## Verifying the Fix

1. After redeployment, check your deployment logs
2. You should see successful connection to your Supabase database
3. Visit your API endpoint (`https://locallift-production.up.railway.app/health`) to verify it's working

## Important Notes

- If you don't know your Supabase PostgreSQL password, you can find it in:
  - Supabase Dashboard → Project Settings → Database
  - Look for "Database Password" section

- Railway environment variables are immediately applied to your project
  - No need to update local files after setting these variables in Railway dashboard

## Using Supabase Connection Pooling

If the above doesn't work, consider enabling connection pooling:

1. In Supabase Dashboard, go to Project Settings → Database
2. Find the "Connection Pooling" section
3. Enable connection pooling
4. Use the provided connection string in your Railway environment variables
