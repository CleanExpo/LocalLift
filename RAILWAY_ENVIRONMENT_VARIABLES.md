# Railway Environment Variables: Complete List

Below is a comprehensive list of all environment variables to set in your Railway deployment. These variables are essential for proper connection to Supabase and overall application functionality.

## Direct PostgreSQL Connection Variables

These variables control the direct database connection using PostgreSQL:

```
# Force IPv4 connections
POSTGRES_CONNECTION_OPTION=-c AddressFamily=inet

# Database connection details
SUPABASE_DB_HOST=52.0.91.163
SUPABASE_DB_PORT=5432
SUPABASE_DB_USER=postgres
SUPABASE_DB_PASSWORD=Sanctuary2025!@
DATABASE_URL=postgresql://postgres:Sanctuary2025!%40@52.0.91.163:5432/postgres?sslmode=require
```

## Supabase API Connection Variables

These variables enable connection via the Supabase REST API (alternative approach):

```
# Supabase connection details
SUPABASE_URL=https://rsooolwhapkkkwbmybdb.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJzb29vbHdoYXBra2t3Ym15YmRiIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NDcwODU0NiwiZXhwIjoyMDYwMjg0NTQ2fQ.4z9OqyeU9-CHmDtZwA87ymicFEM-U53yzdeTZwc6KdE
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJzb29vbHdoYXBra2t3Ym15YmRiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDQ3MDg1NDYsImV4cCI6MjA2MDI4NDU0Nn0.hKGvTKiT0c8270__roY4C66P5haZuXwBpbRSvmpYa34
SUPABASE_JWT_SECRET=O4Lav0c7w2IvacWLVaON8Dl3Expl6RDlIUiTLjsyF9tJR78RHtwqEMZG6Hh8ZdCqsWkx6arpwNxt75PZ3heRvg==
SUPABASE_PROJECT_ID=rsooolwhapkkkwbmybdb
```

To find your Supabase service role key:
1. Log into Supabase dashboard
2. Go to Project Settings > API
3. Copy the "service_role key" (treat this as sensitive)

## Application Configuration Variables

These variables control application behavior and settings:

```
# Application environment
NODE_ENV=production
ENVIRONMENT=production

# Server settings
PORT=8080
HOST=0.0.0.0
WEB_CONCURRENCY=2

# Authentication
JWT_SECRET=O4Lav0c7w2IvacWLVaON8Dl3Expl6RDlIUiTLjsyF9tJR78RHtwqEMZG6Hh8ZdCqsWkx6arpwNxt75PZ3heRvg==

# Frontend URL for CORS and redirects
FRONTEND_URL=https://local-lift-adjm0ahjv-admin-cleanexpo247s-projects.vercel.app
```

## Other Important Variables

These may be needed depending on your specific implementation:

```
# Logging level
LOG_LEVEL=info

# API versioning
API_VERSION=v1

# Email settings (if applicable)
SMTP_HOST=your-smtp-host
SMTP_PORT=587
SMTP_USER=your-smtp-user
SMTP_PASSWORD=your-smtp-password
EMAIL_FROM=noreply@locallift.com

# API rate limiting
RATE_LIMIT_MAX=100
RATE_LIMIT_WINDOW_MS=60000
```

## Instructions for Setting Variables

1. Go to Railway dashboard: https://railway.app/project/0e58b112-f5f5-4285-ad1f-f47d1481045b
2. Navigate to your service (humorous-serenity)
3. Click on the "Variables" tab
4. Add or update each variable with the appropriate value
5. Click "Save Variables"
6. Redeploy your application after saving

## Important Notes

1. At minimum, you need to set the **Direct PostgreSQL Connection Variables** to resolve the IPv6 connection issue
2. If direct PostgreSQL connection continues to fail after setting these variables, set up the **Supabase API Connection Variables** as an alternative approach
3. Sensitive variables (passwords, keys) should be treated securely
4. After setting these variables, the connection issue should be resolved

## Testing After Setting Variables

After setting these variables and redeploying:

1. Check the application logs for connection success messages
2. Test the backend: https://local-lift-production.up.railway.app/health
3. Verify the frontend can connect to the backend
