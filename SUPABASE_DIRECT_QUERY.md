# Supabase Direct Queries for Schema Troubleshooting

Use these step-by-step SQL queries to bypass potential issues in the Supabase interface and verify your schema creation. Execute each section separately in the SQL Editor:

## 1. Check If Tables Already Exist (But Aren't Visible)

```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public';
```

This will list all tables in the public schema. If you see the tables like `user_roles` and `customers` in the results, they exist but might not be showing in the UI.

## 2. Create Tables in Small Groups

Execute these blocks one by one to isolate any issues:

### Block 1: Basic Tables

```sql
-- Enable UUID extension
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

-- User Teams Table
CREATE TABLE IF NOT EXISTS public.user_teams (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id) NOT NULL,
  manager_id UUID REFERENCES auth.users(id) NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  UNIQUE(user_id, manager_id)
);
```

### Block 2: More Tables

```sql
-- Temporary Permissions Table
CREATE TABLE IF NOT EXISTS public.temp_permissions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id) NOT NULL,
  permission TEXT NOT NULL,
  granted_by UUID REFERENCES auth.users(id) NOT NULL,
  expiry TIMESTAMP WITH TIME ZONE NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Role Change Logs
CREATE TABLE IF NOT EXISTS public.role_change_logs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id) NOT NULL,
  old_role TEXT NOT NULL,
  new_role TEXT NOT NULL,
  changed_by UUID REFERENCES auth.users(id) NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Activity Logs
CREATE TABLE IF NOT EXISTS public.activity_logs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id),
  action TEXT NOT NULL,
  resource TEXT NOT NULL,
  details JSONB,
  ip_address TEXT,
  user_agent TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);
```

### Block 3: Test If Simple Table Works

If the above blocks have issues, try a very simple table without relationships:

```sql
CREATE TABLE IF NOT EXISTS public.test_table (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);
```

## 3. Verify Auth.Users Table Exists

The foreign key references to auth.users might be causing issues if it doesn't exist:

```sql
SELECT EXISTS (
  SELECT FROM information_schema.tables 
  WHERE table_schema = 'auth' AND table_name = 'users'
);
```

If this returns `false`, you'll need to modify the references in your table definitions.

## 4. Alternative Simple Schema Without Foreign Keys

If you're still having issues, try this simplified schema without foreign key constraints:

```sql
-- Simple User Roles Table without foreign keys
CREATE TABLE IF NOT EXISTS public.user_roles_simple (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL,
  role TEXT NOT NULL DEFAULT 'user',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Simple Customers Table without foreign keys
CREATE TABLE IF NOT EXISTS public.customers_simple (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL,
  email TEXT,
  phone TEXT,
  status TEXT DEFAULT 'active',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);
```

## 5. Check Permissions for Your Supabase User

```sql
SELECT grantee, privilege_type, table_schema, table_name 
FROM information_schema.table_privileges 
WHERE grantee = current_user AND table_schema = 'public';
```

This will show what permissions your current user has.

## Next Steps After Tables Are Created:

Once you confirm tables are being created:

1. Verify in the SQL editor with: `SELECT * FROM public.user_roles;`
2. Try creating your superadmin user directly:
   ```sql
   INSERT INTO public.user_roles (user_id, role)
   VALUES ('your-user-id-here', 'superadmin');
   ```
3. Continue with the Railway environment variable setup

If you continue to encounter issues, consider creating just the essential tables (user_roles, customers) to get the system minimally functional, then add the rest later.
