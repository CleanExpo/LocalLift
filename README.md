# LocalLift

LocalLift is a platform designed to support local businesses through technology and community engagement tools.

## Deployment System Documentation

This project includes a comprehensive deployment system for both the backend (FastAPI on Railway) and frontend (Static files on Vercel). The following documentation guides will help you deploy, monitor, and maintain the LocalLift application.

### Main Documentation

- **[Deployment Guide](./DEPLOYMENT_GUIDE.md)** - Step-by-step manual deployment instructions
- **[GitHub Actions Guide](./GITHUB_ACTIONS_GUIDE.md)** - Automated CI/CD deployment workflow
- **[Railway Deployment](./RAILWAY_DEPLOYMENT.md)** - Specific details for Railway backend deployment

### Tools Reference

The `tools/` directory contains several utilities to help with deployment and maintenance:

- **pre_deploy_check.py** - Validates configuration before deployment
- **check_null_bytes.py** - Detects files with null byte encoding issues
- **fix_null_bytes.py** - Fixes null byte encoding issues
- **cleanup_temp_files.py** - Removes temporary files
- **monitor_deployment.py** - Monitors the health of deployed services

### Deployment Files

The system uses the following key configuration files:

#### Backend (Railway)
- `Dockerfile` - Container configuration
- `railway.json` - Railway project settings
- `railway.toml` - Additional Railway configuration
- `railway_entry.py` - Application entry point
- `.env.railway` - Environment variables template

#### Frontend (Vercel)
- `vercel.json` - Vercel configuration
- `package.json` - Project configuration
- `public/config.js` - Frontend API configuration

## Quick Start

### Using GitHub Actions (Recommended)

1. Set up the required GitHub repository secrets:
   - RAILWAY_TOKEN
   - VERCEL_TOKEN
   - VERCEL_ORG_ID
   - VERCEL_PROJECT_ID

2. Push to the main branch to trigger deployment

See the [GitHub Actions Guide](./GITHUB_ACTIONS_GUIDE.md) for detailed instructions.

### Manual Deployment

1. Run pre-deployment validation:
   ```
   python tools/pre_deploy_check.py --fix
   ```

2. Deploy the backend to Railway:
   ```
   ./deploy-railway.ps1
   ```

3. Deploy the frontend to Vercel:
   ```
   ./deploy-vercel.ps1
   ```

See the [Deployment Guide](./DEPLOYMENT_GUIDE.md) for detailed instructions.

## Troubleshooting

If you encounter deployment issues:

1. Check the pre-deployment validation results
2. Run the deployment monitoring tool:
   ```
   python tools/monitor_deployment.py
   ```
3. Check for null bytes in source files:
   ```
   python tools/check_null_bytes.py .
   ```
4. For persistent issues, refer to the specific deployment guides

## License

© 2025 LocalLift. All rights reserved.
