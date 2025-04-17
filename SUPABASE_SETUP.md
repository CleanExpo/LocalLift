# Supabase Configuration for LocalLift

This document details the Supabase setup and configuration for the LocalLift application.

## Overview

LocalLift uses Supabase as its backend database and authentication system. The application connects to Supabase using environment variables that are set in the deployment environment.

## Required Environment Variables

The following environment variables are required for Supabase integration:

```
SUPABASE_URL=https://{your-project-id}.supabase.co
SUPABASE_ANON_KEY={your-anon-key}
SUPABASE_SERVICE_ROLE_KEY={your-service-role-key}
SUPABASE_PROJECT_ID={your-project-id}
SUPABASE_JWT_SECRET={your-jwt-secret}
```

These variables should be set in the `.env.railway` file for Railway deployment.

## Database Schema

The Supabase database includes the following key tables:

1. **Badges** - Stores user achievement information
2. **Users** - Core user data with authentication information
3. **Regions** - Geographic regions for targeting
4. **Analytics** - Usage and performance metrics
5. **Posts** - User-generated content and templates
6. **Leaderboards** - Competitive ranking data

Database migrations can be found in the `/supabase/migrations/` directory. These include:

- `00001_initial_schema.sql` - Base schema setup
- `20250415_badge_history.sql` - Badge tracking history
- `20250415_achievement_system.sql` - Achievement system
- `20250416_learning_system.sql` - Learning management system
- `20250417_referral_system.sql` - Referral tracking system

## Client Integration

The Supabase client is initialized in `core/supabase/client.py`. This module:

1. Loads environment variables
2. Creates client instances (anonymous and admin)
3. Handles connection errors gracefully
4. Provides helper functions for database operations

The client supports two access levels:
- **Anonymous role** - Limited permissions for client-side operations
- **Service role** - Elevated permissions for server-side operations

## Security Considerations

1. **JWT Authentication** - Secure token-based authentication
2. **Role-Based Access** - Proper permissions for different user types
3. **Service Role Protection** - Admin functions are isolated from client code
4. **Error Handling** - Graceful handling of authentication issues

## Deployment Integration

During deployment:

1. Environment variables are set in Railway
2. The Supabase client connects automatically
3. Health checks verify database connectivity
4. Migration status is logged

For local development, you can use:
```
supabase start
```

This will start a local Supabase instance for development purposes.

## Troubleshooting

If you encounter Supabase connection issues:

1. Verify all environment variables are correctly set
2. Check that the Supabase project is active
3. Ensure your IP is allowed in Supabase network settings
4. Review logs for specific authentication or query errors

For detailed logging during deployment, set the environment variable:
```
DEBUG=True
```

## Migration Management

To apply new migrations:

1. Add SQL files to the `/supabase/migrations/` directory
2. Run migrations using `supabase db push`
3. Verify migration status with `supabase db status`

All migrations are automatically applied during the deployment process.
