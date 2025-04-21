# LocalLift CRM RBAC Deployment Checklist

This comprehensive checklist walks through the final stages of deploying the LocalLift CRM system with Role-Based Access Control (RBAC).

## Deployment Status Summary

✅ Backend API implemented with proper role checks  
✅ Database schema designed with RBAC tables and policies  
✅ Frontend deployed to Vercel  
✅ Backend deployed to Railway  
❌ Railway-Supabase database connection issue (needs manual fix)  
❌ Database migration applied to Supabase  
❌ SuperAdmin user created  

## Step 1: Fix Railway-Supabase Connection

- [ ] Log in to Railway Dashboard
- [ ] Navigate to your LocalLift project
- [ ] Go to Variables tab
- [ ] Add/Update the following variables:

```
SUPABASE_URL=https://rsooolwhapkkkwbmybdb.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJzb29vbHdoYXBra2t3Ym15YmRiIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NDcwODU0NiwiZXhwIjoyMDYwMjg0NTQ2fQ.4z9OqyeU9-CHmDtZwA87ymicFEM-U53yzdeTZwc6KdE
FRONTEND_URL=https://local-lift-adjm0ahjv-admin-cleanexpo247s-projects.vercel.app
JWT_SECRET=superSecretJWTKeyForLocalLiftRBAC2025
```

- [ ] Add the following IPv4 forcing variables:

```
SUPABASE_DB_HOST=db.rsooolwhapkkkwbmybdb.supabase.co
SUPABASE_DB_PORT=5432
SUPABASE_DB_USER=postgres
SUPABASE_DB_PASSWORD=your-postgres-password
DATABASE_URL=postgresql://postgres:your-postgres-password@db.rsooolwhapkkkwbmybdb.supabase.co:5432/postgres?sslmode=require
POSTGRES_CONNECTION_OPTION="-c AddressFamily=inet"
```

- [ ] Redeploy your Railway service (via Deployments tab)

**Reference document:** [MANUAL_RAILWAY_SUPABASE_FIX.md](MANUAL_RAILWAY_SUPABASE_FIX.md)

## Step 2: Apply Database Migration to Supabase

- [ ] Log in to Supabase dashboard
- [ ] Navigate to SQL Editor
- [ ] Open the fixed SQL file: `supabase/migrations/20250419_rbac_schema_fixed.sql`
- [ ] Copy the entire content
- [ ] Paste into the Supabase SQL Editor
- [ ] Execute the SQL

**SQL File:** [20250419_rbac_schema_fixed.sql](supabase/migrations/20250419_rbac_schema_fixed.sql)

## Step 3: Create SuperAdmin User

- [ ] Visit the frontend: https://local-lift-adjm0ahjv-admin-cleanexpo247s-projects.vercel.app/login/
- [ ] Register a new user account
- [ ] Go to Supabase dashboard
- [ ] Navigate to Authentication → Users
- [ ] Find your newly registered user (look for your email)
- [ ] Copy the user ID
- [ ] Execute this SQL in the Supabase SQL Editor:
  ```sql
  INSERT INTO public.user_roles (user_id, role) 
  VALUES ('YOUR-USER-ID', 'superadmin');
  ```

## Step 4: Verify Deployment

- [ ] Run `verify-deployment.ps1` to check component status:
  ```powershell
  .\verify-deployment.ps1
  ```
- [ ] Verify backend health endpoint returns "healthy"
- [ ] Verify frontend is accessible
- [ ] Check Supabase tables exist
- [ ] Login with SuperAdmin account
- [ ] Verify RBAC controls function properly

**Verification Script:** [verify-deployment.ps1](verify-deployment.ps1)

## Step 5: Post-Deployment Tasks

- [ ] Create additional user roles (staff, manager, etc.)
- [ ] Add sample data to test CRM functionality
- [ ] Test user role permissions
- [ ] Create any additional documentation needed
- [ ] Set up any required monitoring

## Troubleshooting

If you encounter any issues during deployment, refer to these resources:

- **Connection issues:** [MANUAL_RAILWAY_SUPABASE_FIX.md](MANUAL_RAILWAY_SUPABASE_FIX.md)
- **SQL issues:** [FINAL_STEPS_MANUAL.md](FINAL_STEPS_MANUAL.md)
- **General deployment guide:** [FINAL_DEPLOYMENT_GUIDE.md](FINAL_DEPLOYMENT_GUIDE.md)
- **Railway environment variables:** [.env.railway](.env.railway)

## URLs & Endpoints

- **Frontend URL:** https://local-lift-adjm0ahjv-admin-cleanexpo247s-projects.vercel.app
- **Backend URL:** https://locallift-production.up.railway.app
- **Backend Health:** https://locallift-production.up.railway.app/health
- **Supabase Dashboard:** https://rsooolwhapkkkwbmybdb.supabase.co
