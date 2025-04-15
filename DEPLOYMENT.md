# LocalLift Deployment Guide

This document outlines the deployment process for the LocalLift platform, including setting up continuous deployment with Railway.

## Deployment Options

LocalLift supports the following deployment options:

1. **Railway** (Recommended for production)
2. **Local Development** (For testing and development)
3. **Manual Deployment** (Alternative production option)

## Railway Deployment

[Railway](https://railway.app) is the recommended platform for deploying LocalLift due to its simplicity, scalability, and integration features.

### Prerequisites

- GitHub account (for CI/CD integration)
- Railway account
- Railway CLI (optional for local testing)

### Setup Railway Project

1. Log in to [Railway Dashboard](https://railway.app)
2. Create a new project
3. Select "Deploy from GitHub repo"
4. Connect your GitHub account and select the LocalLift repository
5. Configure your environment variables (see below)

### Environment Variables

The following environment variables must be set in your Railway project:

```
DATABASE_URL=postgresql://<username>:<password>@<host>:<port>/<database>
SECRET_KEY=<your-secret-key>
API_KEY=<your-api-key>
DOMAIN=<your-domain>
ENVIRONMENT=production
```

Additional optional variables:

```
DEBUG=false
LOG_LEVEL=info
REDIS_URL=redis://<username>:<password>@<host>:<port>
```

### GitHub Actions Integration

We've included a GitHub Actions workflow that automatically deploys changes to Railway whenever code is pushed to the main branch. To enable this:

1. In your Railway project, go to Settings > Generate Deploy Token
2. In your GitHub repository, go to Settings > Secrets > New repository secret
3. Create a secret named `RAILWAY_TOKEN` with the value from step 1

Now, every push to the main branch will trigger automatic deployment.

### Manual Deployment with Railway CLI

For manual deployments or troubleshooting:

1. Install the Railway CLI:
   ```bash
   npm install -g @railway/cli
   ```

2. Log in to your Railway account:
   ```bash
   railway login
   ```

3. Link your local repository to your Railway project:
   ```bash
   railway link
   ```

4. Deploy your application:
   ```bash
   railway up
   ```

## Local Development Setup

For local development and testing:

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/LocalLift.git
   cd LocalLift
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables by creating a `.env` file based on `.env.template`

4. Run the development server:
   ```bash
   # For Unix/Linux/macOS
   ./start.sh
   
   # For Windows
   start.bat
   ```

## Deployment Architecture

LocalLift follows a modern web application architecture:

- **Frontend**: Served as static files through FastAPI
- **Backend API**: FastAPI endpoints
- **Database**: PostgreSQL (via Supabase or direct connection)
- **Cache**: Redis (optional but recommended for production)

### Database Migrations

Database migrations are managed through SQL files in the `supabase/migrations` directory. Railway automatically runs these migrations during deployment.

To run migrations manually:

```bash
python -m core.database.migrate
```

### Static Files

Static files (CSS, JavaScript, images) are served from the `/static` directory. In production, consider using a CDN for improved performance.

## Monitoring and Troubleshooting

Railway provides built-in logs and monitoring. To view logs:

1. Go to your Railway project dashboard
2. Select the deployment you want to monitor
3. Click on "Logs" to view real-time logs

For more detailed monitoring, consider integrating with services like Sentry or Datadog.

## Scaling Considerations

The default Railway deployment is suitable for small to medium workloads. For larger workloads:

1. Increase your database plan in Railway
2. Consider enabling Redis caching
3. Set up a CDN for static assets

## Additional Resources

- [Railway Documentation](https://docs.railway.app/)
- [FastAPI Deployment Guide](https://fastapi.tiangolo.com/deployment/)
- [Supabase Documentation](https://supabase.io/docs)
