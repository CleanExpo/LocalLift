# LocalLift Deployment Guide

This document outlines the deployment process for the LocalLift platform, including setting up continuous deployment with Railway and Supabase integration.

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
- Supabase account (for database, auth, and storage)

### Setup Railway Project

1. Log in to [Railway Dashboard](https://railway.app)
2. Create a new project
   - Project ID: `0e58b112-f5f5-4285-ad1f-f47d1481045b`
   - Project Name: `locallift`
3. Select "Deploy from GitHub repo"
4. Connect your GitHub account and select the LocalLift repository
5. Configure your environment variables (see below)

### Environment Variables

The following environment variables must be set in your Railway project:

```
# Database Configuration
DATABASE_URL=postgresql://<username>:<password>@<host>:<port>/<database>

# Application Configuration
SECRET_KEY=<your-secret-key>
API_KEY=<your-api-key>
DOMAIN=<your-domain>
ENVIRONMENT=production

# Supabase Configuration
SUPABASE_URL=https://rsooolwhapkkkwbmybdb.supabase.co
SUPABASE_KEY=<your-supabase-anon-key>
SUPABASE_SERVICE_KEY=<your-supabase-service-role-key>
SUPABASE_JWT_SECRET=<your-supabase-jwt-secret>
SUPABASE_PROJECT_ID=rsooolwhapkkkwbmybdb

# Railway Configuration
RAILWAY_PROJECT_ID=0e58b112-f5f5-4285-ad1f-f47d1481045b
RAILWAY_STATIC_URL=1
```

Additional optional variables:

```
DEBUG=false
LOG_LEVEL=info
REDIS_URL=redis://<username>:<password>@<host>:<port>
```

### Supabase Integration

LocalLift integrates with Supabase for:

1. **Database**: PostgreSQL database with Row Level Security
2. **Authentication**: User management and JWT-based authentication
3. **Storage**: File storage for user uploads
4. **Realtime**: Realtime subscriptions for collaborative features

To set up Supabase:

1. Create a project at [Supabase](https://supabase.com)
2. Get your project credentials from the API settings page
3. Add those credentials to your Railway environment variables
4. Run migrations to set up your database schema

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
