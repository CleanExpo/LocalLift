# GitHub Actions Deployment Guide for LocalLift

This guide explains how to use the GitHub Actions workflow we've set up for automating the deployment of LocalLift to both Railway (backend) and Vercel (frontend).

## Overview

The GitHub Actions workflow (`.github/workflows/deploy.yml`) provides:

1. Automated validation of your codebase before deployment
2. Deployment to Railway for the backend
3. Deployment to Vercel for the frontend
4. Deployment notifications and status updates

## Setting Up Your Repository

### Required Secrets

For the GitHub Actions workflow to function properly, you need to set up the following secrets in your GitHub repository:

1. **RAILWAY_TOKEN**: Your Railway API token
   - Generate from Railway CLI using `railway login`
   - Or from the Railway dashboard under settings

2. **VERCEL_TOKEN**: Your Vercel API token
   - Generate from the Vercel dashboard under "Account Settings" > "Tokens"

3. **VERCEL_ORG_ID**: Your Vercel organization ID
   - Found in the Vercel dashboard URL or in project settings

4. **VERCEL_PROJECT_ID**: Your Vercel project ID
   - Found in the project settings in Vercel dashboard

### Setting Up Secrets

1. Navigate to your repository on GitHub
2. Go to "Settings" > "Secrets and variables" > "Actions"
3. Click on "New repository secret"
4. Add each of the required secrets listed above

## Using the GitHub Actions Workflow

### Automatic Deployment

The workflow is configured to run automatically when:

- Code is pushed to the `main` branch
- Code is pushed to the `production` branch

This enables:
- Development deployments when merging to `main`
- Production deployments when pushing to `production`

### Manual Deployment

You can also trigger the workflow manually:

1. Navigate to your repository on GitHub
2. Go to the "Actions" tab
3. Select "Deploy LocalLift" workflow from the left sidebar
4. Click "Run workflow" dropdown on the right
5. Choose the branch to deploy
6. Configure deployment options:
   - Deploy backend: Choose whether to deploy to Railway
   - Deploy frontend: Choose whether to deploy to Vercel
7. Click "Run workflow"

## Understanding the Workflow Steps

The workflow consists of several jobs:

### 1. Validate

This job runs first and performs the following steps:
- Checks out the code
- Sets up Python 3.11
- Installs project dependencies
- Runs the pre-deployment validation (`tools/pre_deploy_check.py --fix`)
- Checks for null bytes in source files

### 2. Deploy Backend

This job deploys the backend to Railway:
- Installs Railway CLI
- Logs in using the RAILWAY_TOKEN
- Links the project
- Deploys to Railway
- Performs a health check on the deployed API

### 3. Deploy Frontend

This job deploys the frontend to Vercel:
- Installs Vercel CLI
- Deploys to Vercel with production flag

### 4. Notify

This job notifies about the deployment result:
- Reports successful deployments with URLs
- Reports failed deployments with error details

## Deployment Log and Status

After running the workflow, you can:

1. View the detailed logs for each step
2. Check the deployment status
3. Access the deployed services via the URLs provided in the notification

## Customizing the Workflow

You can customize the workflow by editing `.github/workflows/deploy.yml`:

- Change the branches that trigger automatic deployment
- Modify the validation steps
- Add additional deployment targets
- Customize the notification format
- Add more sophisticated health checks

## Public Repository Deployment

The workflow has been updated to support deployment from a public GitHub repository:

### Security Considerations

When deploying from a public repository, security becomes even more critical:

1. **Explicit Permissions**: The workflow files now include explicit permission settings:
   ```yaml
   permissions:
     contents: read
     actions: write
     deployments: write
   ```
   This limits what the workflow can access, following the principle of least privilege.

2. **Secrets Management**: Continue using GitHub repository secrets for all sensitive information. These remain securely encrypted even in public repositories.

3. **Fork Protection**: The workflow is configured to prevent unauthorized deployments from repository forks.

4. **Status Badges**: The README now includes deployment status badges that show the current state of your workflows.

### Best Practices for Public Repositories

1. **Never commit sensitive data**: Always use GitHub secrets for tokens, passwords, and API keys.
2. **Limit branch access**: Configure branch protection rules for deployment branches.
3. **Review Pull Requests carefully**: Especially check for any changes to workflow files or deployment scripts.
4. **Monitor workflow runs**: Check logs regularly for any unauthorized or unexpected deployments.
5. **Rotate secrets regularly**: Update your Railway and Vercel tokens periodically.

## Troubleshooting

If the workflow fails, check:

1. The workflow logs for detailed error messages
2. The status of your Railway and Vercel accounts
3. The validity of your API tokens
4. The pre-deployment validation results

For persistent issues, you can:
- Run the deployment steps manually using the provided scripts
- Use `tools/monitor_deployment.py` to check the status of your services
- Review the logs in Railway and Vercel dashboards
