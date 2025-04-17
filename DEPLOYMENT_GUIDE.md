# LocalLift Deployment Guide

This guide provides step-by-step instructions for deploying the LocalLift application to Railway (backend) and Vercel (frontend).

## Prerequisites

- Railway CLI installed (`npm install -g @railway/cli`)
- Vercel CLI installed (`npm install -g vercel`)
- Python 3.11+ installed
- Git

## Project Structure

The LocalLift deployment uses a split architecture:

- **Railway**: Hosts the FastAPI backend application in a Docker container
- **Vercel**: Hosts the static frontend files

## Pre-Deployment Checks

Before deploying, run the pre-deployment validation tool to ensure everything is set up correctly:

```bash
python tools/pre_deploy_check.py --fix
```

This tool checks for:
- Files with null bytes that would cause deployment errors
- Required configuration files
- API endpoint configuration

## Backend Deployment (Railway)

The following files have been configured for Railway deployment:

1. `Dockerfile` - Containerizes the FastAPI application
2. `railway.json` - Railway project configuration
3. `railway.toml` - Additional Railway settings
4. `railway_entry.py` - Entry point for the Railway deployment
5. `.env.railway` - Environment variables template for Railway

### Deployment Steps

1. Authenticate with Railway:
   ```bash
   railway login
   ```

2. Link to the project:
   ```bash
   railway link -p 0e58b112-f5f5-4285-ad1f-f47d1481045b
   ```

3. Deploy using the deployment script:
   ```bash
   ./deploy-railway.ps1
   ```

## Frontend Deployment (Vercel)

The following files have been configured for Vercel deployment:

1. `vercel.json` - Configured for SPA routing
2. `package.json` - Configured to bypass build step
3. `public/config.js` and `public/js/config.js` - API endpoint configuration

### Deployment Steps

1. Authenticate with Vercel:
   ```bash
   vercel login
   ```

2. Deploy using the deployment script:
   ```bash
   ./deploy-vercel.ps1
   ```

## Troubleshooting

### Null Bytes in Python Files

If you encounter null byte errors during deployment:

1. Run the cleanup tool:
   ```bash
   python tools/cleanup_temp_files.py --check-null-bytes --delete
   ```

2. Or fix specific files:
   ```bash
   python tools/fix_null_bytes.py file1.py file2.py
   ```

### API Configuration Issues

If the frontend can't connect to the backend:

1. Verify the API URL in `public/js/config.js` points to:
   ```
   https://locallift-production.up.railway.app
   ```

2. Check CORS settings in `.env.railway` to ensure your frontend domain is allowed.

## Maintenance

To update deployments:

1. Make your changes locally
2. Run pre-deployment validation
3. Deploy using the provided scripts

## Created/Modified Files

During the setup process, the following files were created or modified:

- `tools/pre_deploy_check.py` - Comprehensive pre-deployment validation
- `tools/fix_null_bytes.py` - Tool to fix encoding issues
- `tools/cleanup_temp_files.py` - Tool to clean up temporary files
- `deploy-railway.ps1` - Railway deployment script
- `deploy-vercel.ps1` - Vercel deployment script
- `railway_entry.py` - Railway application entry point
- `Dockerfile` - Docker configuration for Railway
- `railway.json` - Railway project configuration
- `railway.toml` - Railway additional settings
- `.env.railway` - Railway environment variables
- `public/js/config.js` - Frontend API configuration
- `public/config.js` - Additional frontend configuration
