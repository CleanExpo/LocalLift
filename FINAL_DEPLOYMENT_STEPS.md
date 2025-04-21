# LocalLift: Final Deployment Steps

This guide provides detailed instructions for deploying the LocalLift application with its split architecture to both Railway (backend) and Vercel (frontend).

## Deployment Overview

The LocalLift application uses a split architecture:
- **Backend**: Hosted on Railway, running Python FastAPI with Supabase integration
- **Frontend**: Hosted on Vercel, serving static HTML/CSS/JS

## Step 1: Deploy Backend to Railway

The backend deployment includes setting up environment variables and ensuring proper database connectivity.

```powershell
# In your LocalLift directory, run:
powershell -File update-railway-db-connection.ps1
```

This script will:
- Set the correct database connection using hostname instead of IP address
- Update all Supabase credentials
- Deploy the application to Railway

**Verification:**
- Backend API should be available at: https://locallift-production.up.railway.app
- You can test it by visiting this URL directly and checking for API responses

## Step 2: Deploy Frontend to Vercel

The frontend deployment includes creating minimal HTML/CSS/JS files for successful deployment.

```powershell
# In your LocalLift directory, run:
powershell -File manual-deploy-steps.ps1
vercel --prod
```

The `manual-deploy-steps.ps1` script will:
- Create essential files (config.js, main.js, style.css)
- Set up a simplified vercel.json configuration

The `vercel --prod` command will:
- Deploy your files to Vercel's production environment
- Provide you with a deployment URL

**Verification:**
- Frontend should be available at the URL provided by Vercel after deployment
- You should see a basic LocalLift interface that connects to your Railway backend

## Step 3: Configure CORS Settings

To ensure the frontend can communicate with the backend, update the CORS settings on Railway:

```powershell
# This step is handled automatically by update-railway-db-connection.ps1
# The script sets the CORS_ORIGINS environment variable to include your Vercel domain
```

## Step 4: Verify Full Application

1. Visit your Vercel domain in a browser
2. Check browser console (F12) for any connection errors to the backend
3. Verify that the frontend can successfully communicate with the backend

## Troubleshooting

### Railway Connection Issues

If the Railway backend cannot connect to Supabase:
- Verify the Supabase URL and credentials in Railway environment variables
- Ensure the database connection string uses the hostname, not IP address
- Check Railway logs for specific error messages

### Vercel Deployment Failures

If Vercel deployment fails:
- Ensure all required files are present in the public directory
- Verify that vercel.json is correctly formatted
- Check that minimal HTML, CSS, and JS files are present and valid

## Next Steps After Deployment

1. **Set up CI/CD**: Configure GitHub Actions for automated deployments
2. **Add monitoring**: Implement health checks and performance monitoring
3. **Improve security**: Set up proper authentication flow between frontend and backend
4. **Enhance frontend**: Incrementally improve the UI with more features

Congratulations on successfully deploying the LocalLift application! Your split architecture deployment provides a solid foundation for future development and scaling.
