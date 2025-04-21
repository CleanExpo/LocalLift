# Admin Creation Query

Great! You've successfully generated a UUID. Now you can use this UUID to create your superadmin user.

## SQL Query to Create Superadmin

Copy and paste this exact query into the Supabase SQL Editor:

```sql
INSERT INTO public.user_roles (user_id, role)
VALUES ('5f04bcbe-ccb1-464e-83fd-e77af4a7f570', 'superadmin');
```

## Verification Query

After running the above query, verify that the superadmin was created correctly by running:

```sql
SELECT * FROM public.user_roles WHERE role = 'superadmin';
```

You should see a result showing your UUID along with the 'superadmin' role.

## Next Steps

1. After confirming your superadmin user was created successfully, update the Railway environment variables as detailed in FINAL_MANUAL_STEPS.md
2. Deploy the application in Railway
3. Test the backend endpoint: https://local-lift-production.up.railway.app/health
4. Test the frontend: https://local-lift-adjm0ahjv-admin-cleanexpo247s-projects.vercel.app
