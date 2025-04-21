# LocalLift CRM: Deployment Completion Checklist

This checklist serves as a final guide to ensure successful deployment of the LocalLift CRM system. Each section outlines key steps required for a complete production deployment.

## 1. Railway Backend Deployment ✅

- [ ] **Environment Variables Setup**
  - [ ] Log into [Railway Dashboard](https://railway.app/project/0e58b112-f5f5-4285-ad1f-f47d1481045b)
  - [ ] Navigate to the service (humorous-serenity)
  - [ ] Set IPv4 connection variables:
    ```
    POSTGRES_CONNECTION_OPTION=-c AddressFamily=inet
    SUPABASE_DB_HOST=52.0.91.163
    SUPABASE_DB_PORT=5432
    SUPABASE_DB_USER=postgres
    SUPABASE_DB_PASSWORD=postgres_password
    DATABASE_URL=postgresql://postgres:postgres_password@52.0.91.163:5432/postgres?sslmode=require
    ```
  - [ ] Save and trigger redeploy

- [ ] **Deployment Verification**
  - [ ] Check deployment logs for successful startup
  - [ ] Verify database connection (logs should show no connection errors)
  - [ ] Test access to API endpoint at: https://locallift-production.up.railway.app/health

## 2. Supabase Database Migration ✅

- [ ] **Schema Migration**
  - [ ] Access [Supabase Dashboard](https://rsooolwhapkkkwbmybdb.supabase.co)
  - [ ] Navigate to SQL Editor
  - [ ] Run the RBAC schema script from `supabase/migrations/20250419_rbac_schema_fixed.sql`
  - [ ] Verify tables are created in Table Editor

- [ ] **Admin User Setup**
  - [ ] Query existing users: `SELECT id, email FROM auth.users;`
  - [ ] Create superadmin role: 
    ```sql
    INSERT INTO public.user_roles (user_id, role)
    VALUES ('YOUR_USER_ID', 'superadmin');
    ```
  - [ ] Verify role creation: `SELECT * FROM public.user_roles WHERE role = 'superadmin';`

## 3. Vercel Frontend Deployment ✅

- [ ] **Frontend Configuration**
  - [ ] Check API endpoints in frontend config point to Railway backend
  - [ ] Verify Supabase connection details are correct

- [ ] **Deployment Verification**
  - [ ] Access frontend at: https://local-lift-adjm0ahjv-admin-cleanexpo247s-projects.vercel.app
  - [ ] Verify all static assets load properly
  - [ ] Test authentication flow
  - [ ] Confirm backend communication works

## 4. End-to-End Testing ✅

- [ ] **Authentication**
  - [ ] Register new user (if applicable)
  - [ ] Login with existing credentials
  - [ ] Test admin access with superadmin user

- [ ] **Core Functionality**
  - [ ] Test dashboard display
  - [ ] Test customer management
  - [ ] Test user role management
  - [ ] Test reports generation

- [ ] **Security Verification**
  - [ ] Confirm HTTPS is working for all endpoints
  - [ ] Test role-based access controls
  - [ ] Verify JWT authentication works

## 5. Global Timezone Support ✅

- [ ] **Backend Configuration**
  - [ ] Verify timezone field exists in user_preferences table
  - [ ] Test timezone conversion logic

- [ ] **Frontend Implementation**
  - [ ] Check timezone selector in user settings
  - [ ] Test date/time display with different timezones

## 6. Final Documentation ✅

- [ ] **Admin Documentation**
  - [ ] Complete administrator guide
  - [ ] Document emergency procedures
  - [ ] Update security guidelines

- [ ] **User Documentation**
  - [ ] Finalize user guide
  - [ ] Create quick-start guide
  - [ ] Document common workflows

## 7. Post-Deployment Setup ✅

- [ ] **Monitoring**
  - [ ] Set up uptime monitoring
  - [ ] Configure error tracking
  - [ ] Implement performance monitoring

- [ ] **Backups**
  - [ ] Configure regular database backups
  - [ ] Test backup restoration procedure
  - [ ] Document backup/restore process

## Notes on Manual Troubleshooting

If you encounter persistent connection issues between Railway and Supabase, try these steps:

1. Directly modify connection.py to hardcode the IPv4 address instead of resolving from hostname
2. Test if the Supabase IP address is correct (currently using 52.0.91.163)
3. Check if your Supabase password is different from the default
4. Try different IPv4 forcing options if the current one doesn't work
5. Review Railway logs for specific connection error details

## Deployment Contact

For urgent deployment issues, contact:
- Backend Support: backendteam@locallift.example.com
- Database Support: dbadmin@locallift.example.com
- Frontend Support: frontendteam@locallift.example.com
