# LocalLift CRM RBAC Deployment Package

This document serves as the main entry point for deploying the LocalLift CRM system with Role-Based Access Control (RBAC). 

## Deployment Status

The system has been mostly deployed, with only a few final manual steps required:

✅ **Completed:**
- Backend API with RBAC implementation
- Database schema with role policies
- Frontend Vercel deployment
- Backend Railway deployment

❌ **Remaining Tasks:**
- Fix Railway-Supabase connection
- Apply fixed database migration
- Create SuperAdmin user
- Verify deployment

## Quick Start Guide

1. **Fix Database Connection Issue:**
   - Follow [MANUAL_RAILWAY_SUPABASE_FIX.md](MANUAL_RAILWAY_SUPABASE_FIX.md)
   - Update Railway environment variables

2. **Apply Database Schema:**
   - Use [supabase/migrations/20250419_rbac_schema_fixed.sql](supabase/migrations/20250419_rbac_schema_fixed.sql)
   - Run in Supabase SQL Editor

3. **Create Admin User:**
   - Register user through frontend
   - Apply SQL to set as superadmin

4. **Verify Deployment:**
   - Run `.\verify-deployment.ps1` 

## Detailed Documentation

- [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) - Step-by-step deployment checklist
- [FINAL_STEPS_MANUAL.md](FINAL_STEPS_MANUAL.md) - Detailed guide for final manual steps
- [MANUAL_RAILWAY_SUPABASE_FIX.md](MANUAL_RAILWAY_SUPABASE_FIX.md) - Guide to fix Railway-Supabase connection
- [FINAL_DEPLOYMENT_GUIDE.md](FINAL_DEPLOYMENT_GUIDE.md) - Complete deployment documentation

## Important URLs

- **Frontend:** https://local-lift-adjm0ahjv-admin-cleanexpo247s-projects.vercel.app
- **Backend:** https://locallift-production.up.railway.app
- **Supabase:** https://rsooolwhapkkkwbmybdb.supabase.co

## RBAC System Overview

The LocalLift CRM implements a comprehensive role-based access control system with five role levels:

1. **User:** Basic dashboard access
2. **Staff:** Additional view access to analytics and reports
3. **Manager:** Team management capabilities
4. **Admin:** System configuration and user management
5. **SuperAdmin:** Full system access

Each role has appropriate permissions enforced at both the API level (through FastAPI dependency injection) and database level (through Row Level Security policies).

## Deployment Architecture

The system uses a three-tier architecture:

```
┌────────────────────┐     ┌────────────────────┐     ┌────────────────────┐
│                    │     │                    │     │                    │
│  Frontend (Vercel) │────▶│  Backend (Railway) │────▶│ Database (Supabase)│
│                    │     │                    │     │                    │
└────────────────────┘     └────────────────────┘     └────────────────────┘
```

- **Frontend:** Static HTML/CSS/JS deployed on Vercel
- **Backend:** FastAPI application on Railway
- **Database:** PostgreSQL on Supabase with RBAC schema

## Troubleshooting

If you encounter issues:

1. **Connection Problems:**
   - Check Railway logs for specific error messages
   - Verify environment variables match those in `.env.railway`
   - Confirm Supabase is accessible from Railway

2. **Authentication Issues:**
   - Verify JWT secret matches between Railway and code
   - Check that token role claims are working (JWT trigger)
   - Test user registration and login functionality

3. **Permission Problems:**
   - Verify user has correct role in `user_roles` table
   - Check RLS policies are correctly applied
   - Test with different user roles to confirm access control

## Support Resources

- Railway Documentation: https://docs.railway.app
- Supabase Documentation: https://supabase.com/docs
- FastAPI Documentation: https://fastapi.tiangolo.com
- Vercel Documentation: https://vercel.com/docs
