# Visual Guide: How to Generate a UUID in Supabase

This step-by-step guide shows exactly how to generate a UUID (Universally Unique Identifier) in Supabase for your superadmin user.

## Step 1: Log into Supabase

1. Go to the Supabase dashboard: https://rsooolwhapkkkwbmybdb.supabase.co
2. Enter your credentials to log in

## Step 2: Go to the SQL Editor

1. Once logged in, find the navigation sidebar on the left
2. Look for "SQL Editor" or a database icon and click on it

## Step 3: Create a New Query

1. In the SQL Editor, look for a "New Query" or "+" button
2. Click it to create a new SQL query

## Step 4: Run the UUID Generation Query

1. In the query editor, type this SQL command:
   ```sql
   SELECT uuid_generate_v4();
   ```

2. Click "Run" or press Ctrl+Enter to execute the query

## Step 5: View and Copy the Generated UUID

1. The query results will appear below the editor, showing something like:

   ```
   | uuid_generate_v4            |
   |----------------------------|
   | a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11 |
   ```

2. That long string (like `a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11`) is your generated UUID
3. Highlight the UUID and copy it (Ctrl+C)

## Step 6: Use the UUID to Create Your SuperAdmin

1. Clear the SQL Editor or create a new query
2. Enter this SQL, replacing the placeholder with your copied UUID:
   ```sql
   INSERT INTO public.user_roles (user_id, role)
   VALUES ('paste-your-uuid-here', 'superadmin');
   ```

3. For example, if your UUID was `a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11`, you would enter:
   ```sql
   INSERT INTO public.user_roles (user_id, role)
   VALUES ('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'superadmin');
   ```

4. Click "Run" to execute this query

## Step 7: Verify the SuperAdmin Was Created

1. Create another new query
2. Enter:
   ```sql
   SELECT * FROM public.user_roles WHERE role = 'superadmin';
   ```
3. Click "Run"
4. You should see a result showing your UUID along with the 'superadmin' role

## Example of What You'll See:

```
-- When you run: SELECT uuid_generate_v4();
-- You'll see a result like:

| uuid_generate_v4                       |
|---------------------------------------|
| a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11 |


-- After running the INSERT query and then the SELECT query:
-- You'll see a result like:

| id                                   | user_id                                | role       | created_at           | updated_at           |
|--------------------------------------|----------------------------------------|------------|----------------------|----------------------|
| 4b13d915-23cf-4a18-a121-8c7e92371cd7| a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11 | superadmin | 2025-04-19 16:57:22  | 2025-04-19 16:57:22  |
```

## Alternative: Use an Online UUID Generator

If you have trouble using the SQL method, you can also:

1. Visit an online UUID generator like https://www.uuidgenerator.net/
2. Click "Generate" to create a version 4 UUID
3. Copy the generated UUID
4. Use it in the SQL insert statement as shown above

Remember: A UUID is just a unique string to identify your admin user. Any valid UUID will work - the important part is using it consistently in the system.
