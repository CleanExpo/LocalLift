# Railway Deployment Guide for LocalLift

This guide provides comprehensive instructions for deploying the LocalLift application to Railway.

## Prerequisites

- Git repository with your LocalLift code
- Railway account (create one at [railway.app](https://railway.app) if needed)
- Railway CLI (installed via `npm i -g @railway/cli`)

## Deployment Steps

### 1. Setup Environment Variables

Before deploying, add the following environment variables to your Railway project through the Railway dashboard:

```
# API Configuration
API_HOST=0.0.0.0
API_PORT=$PORT
DEBUG=False
SECRET_KEY=your-railway-secret-key-here

# Database Configuration
DATABASE_URL=your-database-url-here
DB_URL=your-database-url-here

# Supabase Configuration
SUPABASE_URL=your-supabase-url-here
SUPABASE_ANON_KEY=your-supabase-anon-key-here
SUPABASE_SERVICE_ROLE_KEY=your-supabase-service-role-key-here
SUPABASE_JWT_SECRET=your-supabase-jwt-secret-here
SUPABASE_PROJECT_ID=your-supabase-project-id-here

# CORS Configuration
CORS_ORIGINS=https://local-lift-r7srnfsma-admin-cleanexpo247s-projects.vercel.app,https://local-lift-production.up.railway.app

# Email Configuration
SENDGRID_API_KEY=your-sendgrid-api-key-here
EMAIL_FROM=your-email-address-here
EMAIL_NAME=LocalLift Notifications

# Feature Flags
ENABLE_GAMIFICATION=True
ENABLE_LEADERBOARDS=True
ENABLE_CERTIFICATIONS=True

# Environment
ENVIRONMENT=production

# API Base URL for Production
API_BASE_URL=https://local-lift-production.up.railway.app
```

Note: In Railway, use `$PORT` (not `${PORT}`) as Railway automatically substitutes its dynamic port.

### 2. Automated Deployment (Windows)

Run the PowerShell deployment script:

```powershell
.\deploy-railway.ps1
```

This script will:
- Check if Railway CLI is installed
- Verify you're logged in to Railway
- Commit the latest changes
- Deploy the application to Railway

### 3. Automated Deployment (Linux/Mac)

Run the Bash deployment script:

```bash
bash deploy-railway.sh
```

### 4. Manual Deployment

If you prefer to deploy manually:

1. Ensure the Railway CLI is installed:
   ```
   npm i -g @railway/cli
   ```

2. Login to Railway:
   ```
   railway login
   ```

3. Connect your project:
   ```
   railway link
   ```

4. Deploy the application:
   ```
   railway up
   ```

## Configuration Files

The deployment uses several configuration files:

### railway.json

This file configures Railway's advanced deployment settings:
```json
{
  "$schema": "https://railway.com/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "runtime": "V2",
    "numReplicas": 1,
    "sleepApplication": false,
    "multiRegionConfig": {
      "asia-southeast1-eqsg3a": {
        "numReplicas": 1
      }
    },
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

Key features:
- Uses NIXPACKS builder for optimized builds
- Deploys with V2 runtime for improved performance
- Configures multi-region deployment with Asia Southeast replica
- Prevents application sleep for 24/7 availability
- Sets failure-based restart policy with up to 10 retries

### Dockerfile

The Dockerfile sets up the container environment:
- Uses Python 3.11 base image
- Installs Node.js for frontend dependencies
- Installs Python and Node dependencies
- Sets up environment variables
- Configures the start command

### .env.railway

This file provides environment variables for the Railway deployment, which are then processed by the Dockerfile.

## Verifying Deployment

After deployment, verify your application is running by checking:

1. The Railway dashboard for deployment status
2. The health check endpoint: `https://local-lift-production.up.railway.app/health`
3. The API health check endpoint: `https://local-lift-production.up.railway.app/api/health`

If both endpoints return successful responses, your deployment is working correctly.

## Troubleshooting

### Common Issues

1. **404 Error**: If Railway's health check is failing, verify:
   - The `/health` endpoint exists (which we've added to main.py)
   - Your application is starting correctly (check Railway logs)

2. **NPM or Node.js Issues**: If experiencing NPM-related errors:
   - Check that package.json is correctly formatted
   - The Dockerfile is properly installing dependencies

3. **Environment Variables**: If your application isn't connecting to services:
   - Verify all environment variables are correctly set in Railway
   - Check for any typos or missing values

### Railway Logs

Railway provides detailed logs for debugging:

1. Go to your Railway dashboard
2. Select your LocalLift project
3. Click on the "Deployments" tab
4. Select the most recent deployment
5. View the logs to identify any errors

## Frontend Configuration

The frontend (deployed on Vercel) is configured to use the Railway backend through the `config.js` file, which dynamically selects the appropriate API URL based on the environment.

## Automatic Redeployment

Railway can be configured for automatic deployment on GitHub pushes through their dashboard settings or GitHub Actions workflows.
