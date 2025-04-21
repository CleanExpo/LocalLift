# Complete Deployment Guide for LocalLift

This guide provides a comprehensive overview of deploying the LocalLift application with its split architecture across Vercel (frontend) and Railway (backend).

## Prerequisites

- Railway account and API token
- Vercel account and access token
- Supabase account with project set up
- Git repository for your LocalLift code

## Architecture Overview

LocalLift uses a split architecture:

1. **Frontend (Vercel)**: Static assets, UI components, and client-side code
2. **Backend (Railway)**: API server, Supabase integration, database connections

## Supabase Authentication Configuration

The Supabase authentication has been set up with the following key environment variables:

```
SUPABASE_URL=https://rsooolwhapkkkwbmybdb.supabase.co
SUPABASE_ANON_KEY=[your anon key]
SUPABASE_SERVICE_ROLE_KEY=[your service role key] 
SUPABASE_JWT_SECRET=[your jwt secret]
SUPABASE_PROJECT_ID=rsooolwhapkkkwbmybdb
```

The database schema includes tables for:
- User authentication (via Supabase auth)
- Gamification (achievements, levels, points)
- Leaderboards
- Certifications

## Deployment Process

### Step 1: Deploy Backend to Railway

```powershell
# Run the deployment script which sets the correct environment variables and deploys to Railway
cd LocalLift
powershell -File fix-railway-config.ps1
```

This script will:
1. Log in to Railway
2. Set all necessary environment variables from .env.railway
3. Ensure Supabase configuration is correct
4. Restart any existing service
5. Deploy the application to Railway

### Step 2: Deploy Frontend to Vercel

```powershell
# Deploy the frontend to Vercel
cd LocalLift
powershell -File deploy-vercel.ps1
```

This script will:
1. Set authentication token for Vercel
2. Update config.js to point to the Railway backend URL
3. Build CSS using Tailwind
4. Deploy to Vercel

## Troubleshooting Common Issues

### Railway Deployment Issues

1. **Environment Variables Mismatch**: Ensure that the variable names are consistent between code and environment settings. Especially check that `SUPABASE_SERVICE_ROLE_KEY` is correctly named (not `SUPABASE_SERVICE_ROLE`).

2. **Database Connection Issues**: Verify that the Supabase URL and keys are correctly set in the Railway environment.

3. **Failed Deployments**: Check Railway logs for specific error messages. Common issues include:
   - Missing environment variables
   - Incorrect API endpoints
   - Database migration failures

### Vercel Frontend Issues

1. **CSS Build Failures**: Make sure that Tailwind is correctly installed and configured.

2. **API Connection Issues**: Verify that the config.js file points to the correct Railway backend URL.

3. **Authentication Problems**: Ensure CORS settings include the Vercel domain.

## Monitoring and Maintenance

- Railway provides logs and monitoring at `https://railway.app/project/[your-project-id]`
- Vercel deployment status can be checked at `https://vercel.com/admin-cleanexpo247s-projects/local-lift`
- Supabase database can be monitored at `https://app.supabase.com/project/rsooolwhapkkkwbmybdb`

## Local Development

For local development:

1. Use the `.env` file (not `.env.railway`) which is configured for development
2. Run `npm run build:css` to build Tailwind CSS
3. Start the application with `python main.py`

## Continuous Integration

The GitHub Actions workflow in `.github/workflows/railway-deploy.yml` automates deployment to Railway. When pushing changes to the main branch, the workflow will:

1. Run tests
2. Build the application
3. Deploy to Railway

## Security Considerations

- API keys and secrets are stored in environment variables, not in the codebase
- Production variables should only be set through the Railway dashboard or deployment scripts
- Supabase service role key provides admin access and should be kept secure
