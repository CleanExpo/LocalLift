# Database Connection Troubleshooting

Based on the deployment logs, we still have a database connection issue. The application has started, but can't connect to the database. Let's troubleshoot this systematically.

## Understanding the Error

The error message from the logs:
```
(Background on this error at: https://sqlalche.me/e/20/e3q8)
...
Is the server running on that host and accepting TCP/IP connections?
```

This indicates that the PostgreSQL connection is still failing, even with our IPv4 settings. The application can't reach the database server.

## Step 1: Verify Railway Environment Variables

First, make sure all environment variables are correctly set in Railway:

1. Check these exact variables in the Railway dashboard:
   ```
   POSTGRES_CONNECTION_OPTION=-c AddressFamily=inet
   SUPABASE_DB_HOST=52.0.91.163
   SUPABASE_DB_PORT=5432
   SUPABASE_DB_USER=postgres
   SUPABASE_DB_PASSWORD=Sanctuary2025!
   DATABASE_URL=postgresql://postgres:Sanctuary2025!@52.0.91.163:5432/postgres?sslmode=require
   ```

2. Ensure there are no typos or formatting issues
3. Also verify other important variables are set:
   - SUPABASE_URL
   - SUPABASE_SERVICE_ROLE_KEY

## Step 2: Check Supabase Database Settings

1. Log into Supabase dashboard: https://rsooolwhapkkkwbmybdb.supabase.co
2. Go to Project Settings > Database
3. Check these settings:
   - Verify the database is active
   - Check if there are IP allow/deny lists that might be blocking Railway
   - Ensure connections from external sources are allowed

## Step 3: Verify IP Address and Connection Details

The IP address we're using (52.0.91.163) might be incorrect or may have changed:

1. In the Supabase dashboard, find the correct database connection details
2. Go to Project Settings > Database > Connection Info
3. Look for the Host address and verify it matches what we're using
4. Update your DATABASE_URL and SUPABASE_DB_HOST if needed

## Step 4: Test Connection Parameters

Create a simple connection test script for local testing:

```python
import psycopg2

try:
    # Test connection
    connection = psycopg2.connect(
        host="52.0.91.163",
        port="5432",
        database="postgres",
        user="postgres",
        password="Sanctuary2025!",
        connect_timeout=10
    )
    
    # If connected, print success
    print("Successfully connected to Supabase!")
    cursor = connection.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    print(f"PostgreSQL version: {version[0]}")
    
    # Close connection
    cursor.close()
    connection.close()
    
except Exception as e:
    print(f"Error connecting to Supabase: {e}")
```

## Step 5: Alternative Connection Approach

If direct connection still fails, try using Supabase's REST API instead of direct PostgreSQL connection:

1. Update your connection.py to use the Supabase API client
2. Set up connection using SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY
3. This approach bypasses direct PostgreSQL connection issues

Example of using Supabase client instead of SQLAlchemy:

```python
from supabase import create_client
import os

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# Create client
supabase = create_client(supabase_url, supabase_key)

# Example query
response = supabase.table("user_roles").select("*").execute()
```

## Step 6: Railway Network Configuration

Check if Railway has network configuration options:

1. Look for settings related to outbound connections
2. Check if there are options to specify egress IP addresses
3. See if there are VPC or networking settings that might affect connections

## Next Steps After Fixing Connection

Once the connection is working:

1. Test the backend API endpoint: https://local-lift-production.up.railway.app/health
2. Verify it returns a success response without database errors
3. Test the frontend: https://local-lift-adjm0ahjv-admin-cleanexpo247s-projects.vercel.app
4. Check if the frontend can successfully communicate with the backend
