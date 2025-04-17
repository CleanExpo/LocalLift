# Setting Up GitHub Secrets for LocalLift Deployment

To enable automated deployment through GitHub Actions, you need to set up the following secrets in your GitHub repository. These secrets are essential for the CI/CD workflow to authenticate with Railway and Vercel.

## Required Secrets

1. **RAILWAY_TOKEN**: API token for Railway deployments
2. **VERCEL_TOKEN**: API token for Vercel deployments
3. **VERCEL_ORG_ID**: Your Vercel organization ID
4. **VERCEL_PROJECT_ID**: Your Vercel project ID

## Step-by-Step Instructions

### 1. Getting Your RAILWAY_TOKEN

1. Install the Railway CLI (if not already installed)
   ```bash
   npm install -g @railway/cli
   ```

2. Login to Railway
   ```bash
   railway login
   ```

3. After login, your token will be stored in:
   - Windows: `%USERPROFILE%/.railway/config.json`
   - macOS/Linux: `~/.railway/config.json`

4. Open this file and copy the `token` value

### 2. Getting Your VERCEL_TOKEN

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click on your profile picture → Settings
3. Go to "Tokens" section
4. Click "Create" to generate a new token
5. Name it "LocalLift GitHub Actions"
6. Choose the "Full Access" scope
7. Click "Create Token" and copy the generated token

### 3. Getting Your VERCEL_ORG_ID

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click on your organization name in the top-left
3. Look at the URL in your browser
4. Your Organization ID is in the URL: `https://vercel.com/[org-name]?[org-id]`
   Extract the `org-id` value (after the `?` character)

### 4. Getting Your VERCEL_PROJECT_ID

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Select the LocalLift project
3. Go to "Settings" tab
4. Scroll down to find "Project ID"
5. Copy this value

### 5. Adding Secrets to GitHub Repository

1. Go to your GitHub repository: https://github.com/CleanExpo/LocalLift
2. Click on "Settings" tab
3. In the left sidebar, click on "Secrets and variables" → "Actions"
4. Click "New repository secret" to add each secret:

   a. Add RAILWAY_TOKEN:
      - Name: `RAILWAY_TOKEN`
      - Value: [Your Railway Token]
      - Click "Add secret"

   b. Add VERCEL_TOKEN:
      - Name: `VERCEL_TOKEN`
      - Value: [Your Vercel Token]
      - Click "Add secret"
      
   c. Add VERCEL_ORG_ID:
      - Name: `VERCEL_ORG_ID`
      - Value: [Your Vercel Organization ID]
      - Click "Add secret"
      
   d. Add VERCEL_PROJECT_ID:
      - Name: `VERCEL_PROJECT_ID`
      - Value: [Your Vercel Project ID]
      - Click "Add secret"

## Verifying Secret Setup

After adding all secrets, you can verify they are properly set up:

1. Go to the "Actions" tab in your GitHub repository
2. Click on "Deploy LocalLift" workflow
3. Click "Run workflow" → "Run workflow"
4. Monitor the workflow run to ensure it can access all required secrets

If the workflow completes successfully, your secrets are correctly configured. If it fails with authentication errors, check the corresponding secret values.

## Security Notes

- Never commit these tokens directly to your code
- Periodically rotate your tokens for better security
- Use the minimum required permissions for your tokens
