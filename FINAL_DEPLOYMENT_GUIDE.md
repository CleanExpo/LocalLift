# LocalLift CRM Complete Deployment Guide

This guide provides comprehensive instructions for deploying the full LocalLift CRM stack, including:
- Supabase database with RBAC schema
- Backend API on Railway
- Frontend UI on Vercel

## Architecture Overview

The LocalLift CRM system consists of three main components:

1. **Supabase Database**
   - PostgreSQL database with Row Level Security (RLS)
   - User authentication system
   - Role-based access control tables
   - CRM data tables

2. **Backend API (Railway)**
   - FastAPI application
   - Authentication endpoints
   - User management
   - Dashboard data services
   - Permission enforcement

3. **Frontend UI (Vercel)**
   - Static HTML/CSS/JS files
   - Role-aware components
   - Dashboard interfaces
   - Authentication UI

## Prerequisites

Before starting the deployment, ensure you have:

- [Git](https://git-scm.com/) installed
- [Railway CLI](https://docs.railway.app/develop/cli) installed and configured
- [Vercel CLI](https://vercel.com/docs/cli) installed and configured
- A [Supabase](https://supabase.com/) account with a new project
- Command-line access to your development environment

## Step 1: Apply Supabase Database Migration

The first step is to set up your Supabase database with the RBAC schema.

### Option 1: Using the Migration Script

1. Run the simplified migration script:
   ```powershell
   .\basic-supabase-migration.ps1
   ```

2. Follow the on-screen instructions to manually apply the migration.

### Option 2: Manual Migration

1. Log in to your Supabase dashboard at https://rsooolwhapkkkwbmybdb.supabase.co
2. Navigate to the SQL Editor
3. Open the migration file: `./supabase/migrations/20250419_rbac_schema.sql`
4. Copy the contents and paste into the SQL Editor
5. Execute the SQL to create the RBAC schema

### Verification

After applying the migration, verify that the tables have been created:

1. In the Supabase dashboard, go to the Table Editor
2. You should see tables including:
   - `user_roles`
   - `user_teams`
   - `temp_permissions`
   - `user_profiles`
   - `customers`
   - And others from the migration

## Step 2: Configure Environment Variables

The deployment scripts will automatically create and update environment variables, but you can also do this manually:

### Railway Environment Variables

Create or update `.env.railway` with:
```
SUPABASE_URL=https://rsooolwhapkkkwbmybdb.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJzb29vbHdoYXBra2t3Ym15YmRiIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NDcwODU0NiwiZXhwIjoyMDYwMjg0NTQ2fQ.4z9OqyeU9-CHmDtZwA87ymicFEM-U53yzdeTZwc6KdE
FRONTEND_URL=https://local-lift-fxu1otnh4-admin-cleanexpo247s-projects.vercel.app
JWT_SECRET=superSecretJWTKeyForLocalLiftRBAC2025
```

### Frontend Configuration

Create or update `./public/js/config.js` with:
```javascript
/**
 * Configuration for LocalLift CRM Frontend
 */
const config = {
  API_BASE_URL: 'https://locallift-production.up.railway.app/api',
  SUPABASE_URL: 'https://rsooolwhapkkkwbmybdb.supabase.co',
  SUPABASE_ANON_KEY: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJzb29vbHdoYXBra2t3Ym15YmRiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDQ3MDg1NDYsImV4cCI6MjA2MDI4NDU0Nn0.RHb4rImTrVqbgAbxZ-LlrEwQ0o42aRDPrco-dY-8dOQ',
  VERSION: '1.0.0',
  ENVIRONMENT: 'production'
};

// Make config available globally
window.config = config;
```

## Step 3: Deploy Backend to Railway

The backend consists of FastAPI endpoints that handle authentication, user management, and dashboard data.

### Option 1: Using the Complete Deployment Script

1. Run the complete deployment script which handles Railway deployment:
   ```powershell
   .\deploy-completed.ps1
   ```

2. Follow the on-screen instructions for Railway deployment.

### Option 2: Manual Railway Deployment

1. Ensure you have the following files:
   - `Procfile` (with `web: uvicorn backend.main:app --host 0.0.0.0 --port $PORT`)
   - `requirements.txt` (with all Python dependencies)
   - `railway.json` (with deployment configuration)

2. Login to Railway CLI:
   ```
   railway login
   ```

3. Link your project (or create a new one):
   ```
   railway link
   ```
   
4. Deploy to Railway:
   ```
   railway up
   ```

### Verification

1. After deployment, Railway will provide a URL for your service
2. Access the URL in a browser to verify the API is running
3. You should see a welcome message or be redirected to the API docs
4. Test the health endpoint: `https://your-railway-url.up.railway.app/health`

## Step 4: Deploy Frontend to Vercel

The frontend consists of static HTML, CSS, and JavaScript files that provide the user interface.

### Option 1: Using the Complete Deployment Script

1. Continue with the deployment script which will handle Vercel deployment:
   ```powershell
   # If you're already running deploy-completed.ps1, just continue with it
   ```

2. Follow the on-screen instructions for Vercel deployment.

### Option 2: Manual Vercel Deployment

1. Login to Vercel CLI:
   ```
   vercel login
   ```

2. Deploy to Vercel:
   ```
   vercel --prod
   ```

### Verification

1. After deployment, Vercel will provide a URL for your site
2. Access the URL in a browser to verify the frontend is running
3. You should see the login page
4. Ensure the frontend can connect to the backend API

## Step 5: Set Up SuperAdmin User

To access the full functionality of the CRM, you need to create a SuperAdmin user:

1. Register a new user through the login page at your Vercel URL
2. Go to your Supabase dashboard
3. Navigate to Authentication > Users to find your user ID
4. Navigate to the SQL Editor and run:
   ```sql
   INSERT INTO public.user_roles (user_id, role) VALUES ('YOUR-USER-ID', 'superadmin');
   ```

## Troubleshooting

### Database Migration Issues

- **Table already exists errors**: You can safely ignore these if running the migration multiple times.
- **Permission errors**: Ensure you're using the correct Supabase service role key.
- **Function errors**: If you encounter errors with functions, try creating them individually in the SQL editor.

### Railway Deployment Issues

- **Build errors**: Check your `requirements.txt` file for compatibility issues.
- **Runtime errors**: Check the logs in Railway dashboard for details.
- **Environment variable issues**: Verify all required environment variables are set in Railway.

### Vercel Deployment Issues

- **Build errors**: Check your frontend code for any issues.
- **API connection issues**: Verify the `API_BASE_URL` in your config points to the correct Railway URL.
- **Authentication issues**: Ensure Supabase credentials are correct in the config.

## Post-Deployment Tasks

After successfully deploying all components:

1. **Create additional users**:
   - Register users through the login page
   - Assign appropriate roles using SQL or the admin interface

2. **Test RBAC functionality**:
   - Log in with different role accounts
   - Verify access restrictions work as expected
   - Test dashboard functionality with various permissions

3. **Data setup**:
   - Add initial customer data
   - Set up team structures
   - Configure dashboard layouts

## Regular Maintenance

To keep your deployment running smoothly:

1. **Monitor logs**:
   - Check Railway logs for backend issues
   - Review Supabase logs for database errors

2. **Update dependencies**:
   - Periodically update Python packages
   - Keep frontend libraries current

3. **Backup data**:
   - Set up regular database backups in Supabase

## Support and Resources

- **Supabase Documentation**: [https://supabase.com/docs](https://supabase.com/docs)
- **Railway Documentation**: [https://docs.railway.app](https://docs.railway.app)
- **Vercel Documentation**: [https://vercel.com/docs](https://vercel.com/docs)
- **FastAPI Documentation**: [https://fastapi.tiangolo.com](https://fastapi.tiangolo.com)

## Conclusion

By following this guide, you've deployed a complete CRM system with:

- A secure database with role-based access control
- A robust backend API for handling business logic
- A user-friendly frontend interface

Your LocalLift CRM is now ready to use and can be accessed at your Vercel URL.
