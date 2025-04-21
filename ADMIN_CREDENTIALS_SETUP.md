# Setting Up Your Master Admin Credentials

This guide explains how to ensure your specified admin credentials are set up correctly in the production system.

## Your Credentials

```
Username: phill.m@carsi.com.au
Password: Sanctuary2025!@#
```

## Setup Process

Since LocalLift CRM uses Supabase for authentication, user credentials are registered through the frontend and then assigned roles in the database. Follow these steps to ensure your credentials are properly set up:

### 1. Register Your Account

1. Visit the production frontend: https://local-lift-adjm0ahjv-admin-cleanexpo247s-projects.vercel.app/login/
2. Click on "Register" or "Sign Up"
3. Enter your email: `phill.m@carsi.com.au`
4. Set your password: `Sanctuary2025!@#`
5. Complete the registration process

### 2. Assign SuperAdmin Role

After registration, you need to manually assign the superadmin role to your account:

1. Log in to Supabase dashboard: https://rsooolwhapkkkwbmybdb.supabase.co
2. Navigate to Authentication → Users
3. Find your user (search for `phill.m@carsi.com.au`)
4. Copy your user ID (UUID)
5. Navigate to SQL Editor
6. Execute the following SQL (replacing YOUR-USER-ID with the UUID you copied):

```sql
INSERT INTO public.user_roles (user_id, role) 
VALUES ('YOUR-USER-ID', 'superadmin');
```

### 3. Verify Access

1. Log out (if currently logged in)
2. Log in with your credentials:
   - Email: `phill.m@carsi.com.au`
   - Password: `Sanctuary2025!@#`
3. Verify you have superadmin access by checking that you can access all admin features

## Important Security Notes

1. **Password Storage**: Your password is securely stored in Supabase (hashed, not plaintext)
2. **Environment Variables**: Your credentials are not stored in any environment variables or configuration files
3. **Credentials Documentation**: Consider moving this file to a secure location after setup, as it contains sensitive information
4. **Password Rotation**: For enhanced security, establish a policy for periodic password rotation

## Troubleshooting

If you face any issues with your credentials:

1. **Password Reset**: Use the "Forgot Password" feature on the login page
2. **Role Assignment**: If superadmin permissions aren't working, verify your role in Supabase:
   ```sql
   SELECT * FROM public.user_roles WHERE user_id = 'YOUR-USER-ID';
   ```
3. **New Account**: If necessary, you can create a new superadmin account and disable the original one

## Next Steps After Verification

Once you've confirmed your admin access is working:

1. Create additional administrator accounts as backups
2. Set up other user accounts with appropriate roles
3. Configure system settings using your admin access
4. Begin using the CRM with your sample data for testing
