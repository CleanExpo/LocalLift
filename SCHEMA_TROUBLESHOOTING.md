# Troubleshooting Supabase Schema Creation

If the tables like `user_roles`, `user_teams`, and `customers` are not appearing in the Table Editor after running the SQL script, follow these steps:

## 1. Check for SQL Execution Errors

When executing a large SQL script, errors might occur but might not be immediately visible:

1. **Review SQL Editor Output**:
   - Look at the output/console area in the SQL Editor after execution
   - Check for any red error messages or warnings
   - Pay attention to specific line numbers or syntax issues mentioned

2. **Execute in Smaller Batches**:
   - Try running the SQL script in smaller sections
   - Begin with just the extension and first few tables:
     ```sql
     -- Enable UUID extension if not already enabled
     CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

     -- User Roles Table
     CREATE TABLE IF NOT EXISTS public.user_roles (
       id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
       user_id UUID REFERENCES auth.users(id) NOT NULL,
       role TEXT NOT NULL DEFAULT 'user' CHECK (role IN ('user', 'staff', 'manager', 'admin', 'superadmin')),
       created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
       updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
       UNIQUE(user_id)
     );
     ```
   - Check if this smaller piece executes successfully and creates a table

## 2. Verify Schema and Permissions

1. **Check Schema Selection**:
   - Make sure you're executing the SQL in the correct schema (public)
   - Some Supabase interfaces have a schema selector dropdown

2. **Check Permissions**:
   - Ensure your Supabase account has permissions to create tables
   - You should be using a service role key or be logged in as an administrator

3. **Manually Refresh Table List**:
   - Sometimes the Table Editor doesn't automatically refresh
   - Look for a refresh button or navigate away and back to the Table Editor

## 3. Try Alternative Approaches

1. **Use Supabase CLI** (if available):
   - If you have access to the Supabase CLI, you can try executing the migration through it:
     ```
     supabase db push
     ```

2. **Create a Single Test Table**:
   - Try creating just one simple table to confirm basic table creation works:
     ```sql
     CREATE TABLE IF NOT EXISTS public.test_table (
       id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
       name TEXT,
       created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
     );
     ```

3. **Check for Existing Tables with Same Names**:
   - Run this query to see if the tables already exist but are empty:
     ```sql
     SELECT table_name 
     FROM information_schema.tables 
     WHERE table_schema = 'public';
     ```

## 4. Check for auth.users Table

The SQL references `auth.users` table for foreign keys:

```sql
SELECT EXISTS (
  SELECT FROM information_schema.tables 
  WHERE table_schema = 'auth' AND table_name = 'users'
);
```

If this returns false, you might need to fix the references or create the auth tables first.

## 5. Debug Function Creation Issues

Sometimes function creation can cause issues. Try executing the schema without the functions first:

1. Remove all the `CREATE OR REPLACE FUNCTION` sections temporarily
2. Execute just the table creation statements
3. Once tables are created successfully, add the functions back one by one

## Next Steps After Resolving

Once you've identified and fixed the issue:

1. Confirm tables are visible in the Table Editor
2. Create your SuperAdmin user
3. Continue with updating the Railway environment variables
