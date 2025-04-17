# LocalLift CI/CD Pipeline: Final Setup Steps

Now that all deployment files, scripts, and documentation have been successfully committed to GitHub, follow these steps to complete the CI/CD pipeline setup.

## 1. Configure GitHub Secrets

GitHub Actions requires specific secrets to authenticate with Railway and Vercel. These must be added to your repository settings.

### 1.1 Access Repository Settings

1. Navigate to https://github.com/CleanExpo/LocalLift
2. Click the "Settings" tab at the top of the repository
3. In the left sidebar, click "Secrets and variables" → "Actions"
4. You'll need to add four secrets as detailed below

### 1.2 Add RAILWAY_TOKEN

1. Install the Railway CLI (if not already installed):
   ```bash
   npm install -g @railway/cli
   ```

2. Authenticate with Railway:
   ```bash
   railway login
   ```

3. Find your token in:
   - Windows: `%USERPROFILE%/.railway/config.json`
   - macOS/Linux: `~/.railway/config.json`

4. In GitHub repository settings:
   - Click "New repository secret"
   - Name: `RAILWAY_TOKEN`
   - Value: [copy the token from config.json]
   - Click "Add secret"

### 1.3 Add VERCEL_TOKEN

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click your profile picture → "Settings"
3. Navigate to the "Tokens" section
4. Click "Create" to generate a new token
5. Name: "LocalLift GitHub Actions"
6. Scope: "Full Access"
7. Click "Create Token" and copy the generated token

8. In GitHub repository settings:
   - Click "New repository secret"
   - Name: `VERCEL_TOKEN`
   - Value: [paste the token]
   - Click "Add secret"

### 1.4 Add VERCEL_ORG_ID

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click on your organization name in the top-left
3. Look at the URL in your browser:
   `https://vercel.com/[org-name]?[org-id]`
4. Copy the `org-id` value (after the `?` character)

5. In GitHub repository settings:
   - Click "New repository secret"
   - Name: `VERCEL_ORG_ID`
   - Value: [paste the org-id]
   - Click "Add secret"

### 1.5 Add VERCEL_PROJECT_ID

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Select the LocalLift project
3. Go to "Settings" tab
4. Scroll down to find "Project ID"
5. Copy this value

6. In GitHub repository settings:
   - Click "New repository secret"
   - Name: `VERCEL_PROJECT_ID`
   - Value: [paste the project ID]
   - Click "Add secret"

## 2. Enable GitHub Actions Workflow

1. Go to the "Actions" tab in your GitHub repository
2. You should see the "Deploy LocalLift" workflow listed
3. If it's not already enabled, click "I understand my workflows, go ahead and enable them"

## 3. Trigger First Deployment

Make a minor change to trigger your first automated deployment:

1. Edit a file in your repository (e.g., update README.md with a small change)
2. Commit and push to the main branch:
   ```bash
   git add README.md
   git commit -m "Trigger first automated deployment"
   git push origin main
   ```

## 4. Monitor Deployment Progress

1. Go to the "Actions" tab in your GitHub repository
2. You'll see a new workflow run in progress
3. Click on it to view detailed logs
4. The workflow will deploy:
   - Backend to Railway
   - Frontend to Vercel
   - Run validation checks

## 5. Verify Deployment Success

After the workflow completes:

1. Check Railway deployment:
   - Go to [Railway Dashboard](https://railway.app/dashboard)
   - Verify LocalLift service is running
   - Test the API health endpoint: `YOUR_RAILWAY_URL/api/health`

2. Check Vercel deployment:
   - Go to [Vercel Dashboard](https://vercel.com/dashboard)
   - Click on LocalLift project
   - Click "Visit" to open the deployed site
   - Verify the frontend loads correctly

## 6. Ongoing Development Workflow

For future changes:

1. Make code changes in your local repository
2. Commit and push to the main branch
3. GitHub Actions will automatically:
   - Deploy backend to Railway
   - Deploy frontend to Vercel
   - Run validation checks
   - Report deployment status

## Troubleshooting

If deployments fail:

1. Check the GitHub Actions logs for specific error messages
2. Verify all four secrets are correctly configured
3. Ensure Railway and Vercel tokens have not expired
4. Run the pre-deployment validation tool:
   ```bash
   python tools/pre_deploy_check.py --fix
   ```
5. Check for null bytes in source files:
   ```bash
   python tools/check_null_bytes.py .
   ```

## Conclusion

Your LocalLift application now has:
- Modern deployment infrastructure with containerization
- Comprehensive documentation for all deployment processes
- Fully automated CI/CD pipeline through GitHub Actions
- Health checks and monitoring for reliability
- Git-based version control for all configuration

Simply push changes to the main branch, and the entire application will be automatically deployed.
