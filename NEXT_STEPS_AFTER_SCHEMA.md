# LocalLift CRM: Next Steps After Schema Creation

Great! Now that the database tables have been successfully created, let's continue with the remaining deployment steps:

## 1. Create a SuperAdmin User

Execute the following SQL queries in the Supabase SQL Editor:

```sql
-- Generate a UUID for the admin user if you don't have a specific one
SELECT uuid_generate_v4();

-- Take the generated UUID and insert it as a superadmin
INSERT INTO public.user_roles (user_id, role)
VALUES ('paste-generated-uuid-here', 'superadmin');

-- Verify the superadmin was created
SELECT * FROM public.user_roles WHERE role = 'superadmin';
```

## 2. Update Railway Environment Variables

Now that we have our database schema in place, we need to update the Railway environment variables to use the IPv4 connection:

1. Log into the Railway dashboard (https://railway.app/project/0e58b112-f5f5-4285-ad1f-f47d1481045b)
2. Navigate to your service (humorous-serenity)
3. Click on the "Variables" tab
4. Add or update the following variables:

```
POSTGRES_CONNECTION_OPTION=-c AddressFamily=inet
SUPABASE_DB_HOST=52.0.91.163
SUPABASE_DB_PORT=5432
SUPABASE_DB_USER=postgres
SUPABASE_DB_PASSWORD=Sanctuary2025!
DATABASE_URL=postgresql://postgres:Sanctuary2025!@52.0.91.163:5432/postgres?sslmode=require
```

5. Click "Save Variables"
6. Go to the "Deployments" tab
7. Click "Deploy" to create a new deployment with the updated variables

## 3. Verify the Deployment

Once the Railway application is redeployed:

1. Run the verification script again:
```
.\verify-deployment.ps1
```

2. Check the Railway logs to confirm there are no more IPv6 connection errors
3. Test the backend API endpoint manually by visiting:
```
https://local-lift-production.up.railway.app/health
```

4. Test the frontend by visiting:
```
https://local-lift-adjm0ahjv-admin-cleanexpo247s-projects.vercel.app
```

## 4. Update Database Connection in Backend Code

If you still encounter issues with the IPv6/IPv4 connection after updating the environment variables, you may need to directly modify the database connection code:

1. Open `core/database/connection.py`
2. Look for the database connection setup
3. Add explicit IPv4 configuration:

```python
# Example modification (adjust based on your actual code)
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/postgres")

connect_args = {
    "options": "-c AddressFamily=inet"
}

if "sslmode=require" in SQLALCHEMY_DATABASE_URL:
    connect_args["sslmode"] = "require"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args=connect_args
)
```

4. Save the file and commit the changes
5. Deploy again to Railway

## 5. Final Deployment Checklist

Go through the `COMPLETION_CHECKLIST.md` file to verify all aspects of the deployment:

- Backend deployed successfully to Railway
- Frontend deployed successfully to Vercel
- Database schema applied to Supabase
- SuperAdmin user created
- Database connection using IPv4 works
- Authentication works
- Frontend can communicate with backend
- Basic functionality can be tested

## Important Note on Authentication

Since we've created a simplified schema without auth dependencies, you may need to adjust your authentication system to work with this schema. The current implementation doesn't have foreign key constraints to auth.users, so you'll need to handle user authentication separately.

For immediate testing purposes, you might want to:

1. Create test users directly in the user_roles table
2. Update your authentication logic to use these users
3. Implement proper authentication integration later
