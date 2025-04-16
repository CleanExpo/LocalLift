# LocalLift Deployment Guide

This document outlines the complete deployment process for the LocalLift application, covering both the backend API (FastAPI on Railway) and frontend static site (Vercel).

## Deployment Architecture

LocalLift uses a split deployment architecture:

1. **Backend API**: Dockerized FastAPI application deployed on Railway
2. **Frontend**: Static SPA (Single Page Application) deployed on Vercel

This separation provides several benefits:
- Scalable API backend with containerization
- Optimal performance for static frontend assets
- Independent deployment cycles for frontend and backend
- Cost-effective hosting model

## I. Railway Deployment (Backend)

### Prerequisites

- Railway account
- Railway CLI installed (`npm install -g @railway/cli`)
- Git repository with LocalLift code

### Configuration Files

1. **railway.json**
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
       "restartPolicyMaxRetries": 10,
       "healthcheckPath": "/health",
       "healthcheckTimeout": 10
     }
   }
   ```
   This configuration includes:
   - NIXPACKS builder for optimal build process
   - V2 runtime environment
   - Multi-region deployment with replicas in Asia Southeast region
   - Failure-based restart policy with a maximum of 10 retries
   - Sleep prevention to maintain 24/7 availability
   - Health check configuration pointing to the `/health` endpoint

2. **Dockerfile**
   The Dockerfile is configured with production-grade settings:
   ```
   # Key features of the Docker configuration:
   - Uses Python 3.11-slim-bullseye for minimal image size
   - Runs as non-root user (locallift) for security
   - Includes Docker HEALTHCHECK for container health monitoring
   - Optimized layer caching for faster builds
   - Proper file permissions and directory structure
   - Includes all dependencies with version pinning
   ```

3. **.env.railway**
   Environment variables for production deployment.

### Environment Variables

The following environment variables should be set in the Railway dashboard:

```
SUPABASE_URL
SUPABASE_ANON_KEY
SUPABASE_SERVICE_ROLE
SENDGRID_API_KEY
CORS_ORIGINS=https://locallift-*.vercel.app
LOCALLIFT_AUTH_TOKEN=e6fa0a43-3924-4260-96eb-9e34e4829a58
```

The LocalLift authentication token (`e6fa0a43-3924-4260-96eb-9e34e4829a58`) is automatically set by the deployment scripts. This token is required for API authentication and secure operations.

### Deployment Steps

1. Authenticate with Railway:
   ```
   railway login
   ```

2. Link to the project:
   ```
   railway link -p 0e58b112-f5f5-4285-ad1f-f47d1481045b
   ```

3. Deploy using the secure deployment script:
   ```
   ./deploy-secure.sh
   ```

The script handles linking to the correct project, verifying environment variables, and deploying the application.

### Health Checks

The application provides two health check endpoints:
- `/health` - Root health check for Railway's built-in monitoring (returns a plain text "ok" response)
- `/api/health` - Detailed API health status with feature information (returns JSON)

Railway's health check system requires the `/health` endpoint to return a simple response. This is handled by our specialized `railway_entry.py` entry point, which ensures proper compatibility with Railway's health check system.

### API URL Configuration

The configuration is already set up with the correct Railway URL:

```javascript
// In public/js/config.js
PRODUCTION_API_URL: "https://locallift-production.up.railway.app"
```

This URL is automatically maintained by both the Bash and PowerShell deployment scripts, ensuring your frontend can properly communicate with your backend API.

## II. Vercel Deployment (Frontend)

### Configuration Files

1. **vercel.json**
   ```json
   {
     "cleanUrls": true,
     "rewrites": [
       { "source": "/admin/guide", "destination": "/index.html" },
       { "source": "/(.*)", "destination": "/index.html" }
     ],
     "buildCommand": "",
     "outputDirectory": "public"
   }
   ```

2. **package.json**
   ```json
   {
     "name": "locallift",
     "version": "1.0.0",
     "scripts": {
       "build": "echo 'Static deployment only'"
     },
     "license": "MIT"
   }
   ```

### Static Site Structure

The frontend is a pure static site served from the `/public` directory:

- `public/index.html` - Main SPA entry point
- `public/style.css` - Core styling

### Deployment Steps

1. Prepare the static assets for deployment:
   ```bash
   # Linux/Mac
   ./prepare-vercel-deploy.sh

   # Windows
   .\prepare-vercel-deploy.ps1
   ```
   This script:
   - Creates the necessary directory structure in `/public`
   - Copies `config.js` and other static assets from `/static` to `/public`
   - Updates references in index.html to point to the correct locations

2. Deploy to Vercel using the deployment script:
   ```bash
   # Linux/Mac
   ./deploy-vercel.sh

   # Windows
   .\deploy-vercel.ps1
   ```
   This script:
   - Checks if Vercel CLI is installed
   - Verifies you're logged in to Vercel
   - Builds documentation if needed
   - Deploys the application to Vercel

Alternatively, you can deploy manually with:
```
vercel --prod --yes
```

## III. Local Development

To run the application locally:

1. Start the backend:
   ```
   uvicorn main:app --reload --port 8000
   ```

2. Access the application:
   - API Documentation: http://localhost:8000/docs
   - Admin Guide: http://localhost:8000/admin/guide
   - Sales Dashboard: http://localhost:8000/admin/sales-dashboard

## IV. CI/CD Integration

The GitHub workflow in `.github/workflows/main.yml` validates the environment, runs linting, and tests the startup process.

## V. Important Notes

✅ Vercel and Railway will NOT conflict as long as:
- Railway uses Docker to serve FastAPI
- Vercel is pointed only to /public for static assets
- You do not invoke npm start, since it's not needed
- You do not commit .env (only use .env.template)

🔐 Credentials are stored safely in the respective platform dashboards (not committed to the repository).

🧪 Health checks and SPA fallback ensure smooth deployment and operation.

🗄️ For details on Supabase setup and database migrations, see [SUPABASE_SETUP.md](SUPABASE_SETUP.md).

## Troubleshooting

### Common Issues

1. **API Connection Errors**
   - Verify CORS_ORIGINS in Railway environment variables
   - Check that frontend configuration is pointing to the correct API URL

2. **Deployment Failures**
   - Verify Railway CLI is installed and you're logged in
   - Check that all required environment variables are set
   - Review Railway logs for detailed error information

3. **Static Asset Issues**
   - Ensure all assets are in the public directory
   - Verify the Vercel configuration is correct
