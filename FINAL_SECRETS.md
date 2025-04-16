# LocalLift CI/CD Final Configuration

This document contains the final configuration values needed to set up your GitHub Actions CI/CD pipeline. These values should be added as secrets to your GitHub repository.

## All Required GitHub Secrets

Add the following secrets to your GitHub repository at [github.com/CleanExpo/LocalLift](https://github.com/CleanExpo/LocalLift):

### 1. RAILWAY_TOKEN

```
p 0e58b112-f5f5-4285-ad1f-f47d1481045b
```

This token allows GitHub Actions to deploy your backend to Railway.

### 2. VERCEL_TOKEN

```
jtqL60Dymmd2bbAttw1Yl3ga
```

This token allows GitHub Actions to deploy your frontend to Vercel.

### 3. VERCEL_ORG_ID

```
team_hIVuEbN4ena7UPqg1gt1jb6s
```

This is your Vercel team/organization ID.

### 4. VERCEL_PROJECT_ID

```
prj_i4Oo7FupClayBNt2BQH8noUnu0Hx
```

This is your Vercel project ID for LocalLift.

## How to Add GitHub Secrets

1. Go to your GitHub repository: https://github.com/CleanExpo/LocalLift
2. Navigate to Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Add each of the four secrets above with their corresponding values
5. Ensure you copy the values exactly as shown above, with no extra spaces

## After Adding Secrets

Once all four secrets are added to your GitHub repository, any push to the main branch will automatically:

1. Deploy the backend to Railway
2. Deploy the frontend to Vercel
3. Run validation checks
4. Report deployment status

## Deployment URLs

- Frontend: https://local-lift-5wus1j15e-admin-cleanexpo247s-projects.vercel.app
- Backend API: https://locallift-production.up.railway.app

## Security Note

This document contains sensitive information. After you've added these values to GitHub Secrets, you may want to remove this file from your repository for security purposes.
