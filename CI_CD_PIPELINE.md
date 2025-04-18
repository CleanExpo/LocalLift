# CI/CD Pipeline Documentation

This document provides detailed information about the Continuous Integration and Continuous Deployment (CI/CD) pipeline implemented for the LocalLift platform.

## Table of Contents

- [Overview](#overview)
- [Pipeline Architecture](#pipeline-architecture)
- [Workflow Stages](#workflow-stages)
- [Environment Configuration](#environment-configuration)
- [Deployment Targets](#deployment-targets)
- [Monitoring and Reporting](#monitoring-and-reporting)
- [Managing GitHub Secrets](#managing-github-secrets)
- [Troubleshooting](#troubleshooting)

## Overview

LocalLift implements a comprehensive CI/CD pipeline using GitHub Actions that automates the testing, building, and deployment processes. The pipeline supports multiple environments (development, staging, production) and handles both backend (Railway) and frontend (Vercel) deployments in a coordinated manner.

Key features of the pipeline include:

- Automated quality checks and testing
- Environment-specific build configurations
- Automated deployments to multiple environments
- Post-deployment verification and health checks
- Deployment reports and notifications
- Manual trigger option with customizable parameters

The pipeline is defined in `.github/workflows/ci-cd.yml` and replaces the previous separate deployment workflows.

## Pipeline Architecture

The CI/CD pipeline is structured as a multi-stage workflow with the following high-level components:

```
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│  Pre-Deploy   │     │    Build &    │     │   Deployment  │
│ Quality Checks│────▶│    Package    │────▶│ (Railway/Vercel) │
└───────────────┘     └───────────────┘     └───────────────┘
                                                    │
                                                    ▼
                                           ┌───────────────┐
                                           │ Post-Deploy   │
                                           │ Verification  │
                                           └───────────────┘
```

The workflow is triggered by:
- Pushes to main, staging, or development branches
- Pull requests to main or staging branches
- Manual workflow dispatch with customizable parameters

## Workflow Stages

### 1. Quality Checks

This stage runs a series of automated checks to ensure code quality and prevent issues before deployment:

- **Code linting**: Checks for syntax errors and coding standards
- **Security scanning**: Uses Bandit to detect security vulnerabilities
- **Null byte detection**: Ensures files don't contain null bytes that could cause issues
- **Pre-deployment validation**: Runs custom validation script to verify deployment readiness

```yaml
quality-checks:
  name: Quality Checks
  runs-on: ubuntu-latest
  steps:
    - name: Checkout code
      uses: actions/checkout@v3
      
    # Python setup, linting, security scanning, etc.
    # ...
```

### 2. Automated Testing

Runs comprehensive tests to verify functionality:

- **Python tests**: Runs pytest with coverage reporting
- **Frontend tests**: Executes npm test if available
- **Coverage reporting**: Uploads coverage data to codecov

```yaml
test:
  name: Run Tests
  needs: quality-checks
  runs-on: ubuntu-latest
  steps:
    # Python & Node.js setup
    # ...
    
    - name: Run Python tests with coverage
      run: |
        pytest --cov=./ --cov-report=xml
    
    # Frontend tests, coverage uploads, etc.
    # ...
```

### 3. Build and Package

Prepares the application for deployment:

- **Environment detection**: Determines the target environment
- **Build ID generation**: Creates a unique identifier for the build
- **Asset preparation**: Collects static assets and builds frontend resources
- **Artifact creation**: Packages backend and frontend components separately

```yaml
build:
  name: Build
  needs: test
  runs-on: ubuntu-latest
  outputs:
    build_id: ${{ steps.set-build-id.outputs.build_id }}
  steps:
    # Environment setup, dependency installation
    # ...
    
    - name: Set build ID
      id: set-build-id
      run: |
        BUILD_ID="${{ github.sha }}-$(date +%s)"
        echo "BUILD_ID=$BUILD_ID" >> $GITHUB_ENV
        echo "build_id=$BUILD_ID" >> $GITHUB_OUTPUT
    
    # Build frontend assets, create deployment artifacts
    # ...
```

### 4. Backend Deployment

Deploys the backend to Railway:

- **Environment selection**: Configures the deployment for the target environment
- **Railway linking**: Associates the workflow with the correct Railway project
- **Deployment**: Executes the Railway deployment
- **Health check**: Verifies the deployed backend is functioning

```yaml
deploy-backend:
  name: Deploy Backend to Railway
  needs: [build]
  if: success() && (github.event_name != 'pull_request') && (github.event.inputs.deploy_backend != 'false')
  runs-on: ubuntu-latest
  environment:
    name: ${{ github.event.inputs.environment || (github.ref == 'refs/heads/main' && 'production') || ... }}
    url: https://locallift-${{ ... }}.up.railway.app
  steps:
    # Download artifacts, extract, railway setup
    # ...
    
    - name: Deploy to Railway
      working-directory: deploy
      run: |
        railway up --detach --service "locallift-${{ env.DEPLOY_ENV }}"
      env:
        RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
        BUILD_ID: ${{ needs.build.outputs.build_id }}
    
    # Health check, notification
    # ...
```

### 5. Frontend Deployment

Deploys the frontend to Vercel:

- **Environment configuration**: Sets up the frontend for the target environment
- **API URL configuration**: Updates configuration to point to the correct backend
- **Vercel deployment**: Executes the Vercel deployment
- **Deployment verification**: Confirms the frontend is accessible

```yaml
deploy-frontend:
  name: Deploy Frontend to Vercel
  needs: [build, deploy-backend]
  if: success() && (github.event_name != 'pull_request') && (github.event.inputs.deploy_frontend != 'false')
  runs-on: ubuntu-latest
  environment:
    name: ${{ ... }}
    url: https://local-lift-${{ ... }}.vercel.app
  steps:
    # Download artifacts, configure backend URL
    # ...
    
    - name: Deploy to Vercel
      working-directory: deploy
      run: |
        if [[ "${{ env.DEPLOY_ENV }}" == "production" ]]; then
          vercel deploy --prod --yes --token ${{ secrets.VERCEL_TOKEN }}
        else
          vercel deploy --yes --token ${{ secrets.VERCEL_TOKEN }}
        fi
      env:
        VERCEL_TOKEN: ${{ secrets.VERCEL_TOKEN }}
        VERCEL_ORG_ID: ${{ secrets.VERCEL_ORG_ID }}
        BUILD_ID: ${{ needs.build.outputs.build_id }}
    
    # Deployment verification, notification
    # ...
```

### 6. Post-Deployment Tasks

Executes tasks after successful deployment:

- **Deployment report**: Creates a summary of the deployment
- **Notification**: Provides deployment details
- **Artifact upload**: Stores the deployment report for future reference

```yaml
post-deploy:
  name: Post-deployment Tasks
  needs: [deploy-backend, deploy-frontend]
  if: success() && github.event_name != 'pull_request'
  runs-on: ubuntu-latest
  steps:
    # Create deployment report, send notifications
    # ...
```

### 7. Deployment Monitoring

For production deployments, monitors the application health after deployment:

- **Periodic checks**: Monitors key endpoints for a specified duration
- **Performance metrics**: Collects performance data
- **Results reporting**: Stores monitoring results as artifacts

```yaml
monitor:
  name: Monitor Deployment
  needs: [deploy-backend, deploy-frontend]
  if: success() && github.ref == 'refs/heads/main'
  runs-on: ubuntu-latest
  steps:
    # Setup monitoring dependencies, run monitoring script
    # ...
```

## Environment Configuration

The pipeline supports three environments:

### Development

- **Trigger**: Push to development branch or manual dispatch with environment=development
- **Railway Project**: d27fc113-a812-49b5-a791-4e7b9c7a1234
- **Vercel Project**: Uses VERCEL_PROJECT_ID_DEV secret
- **URL Pattern**: 
  - Backend: https://locallift-development.up.railway.app
  - Frontend: https://local-lift-development.vercel.app

### Staging

- **Trigger**: Push to staging branch or manual dispatch with environment=staging
- **Railway Project**: ba36c743-97f2-4f3f-a888-5aa91c5a9e23
- **Vercel Project**: Uses VERCEL_PROJECT_ID_STAGING secret
- **URL Pattern**:
  - Backend: https://locallift-staging.up.railway.app
  - Frontend: https://local-lift-staging.vercel.app

### Production

- **Trigger**: Push to main branch or manual dispatch with environment=production
- **Railway Project**: 0e58b112-f5f5-4285-ad1f-f47d1481045b
- **Vercel Project**: Uses VERCEL_PROJECT_ID_PROD secret
- **URL Pattern**:
  - Backend: https://locallift-production.up.railway.app
  - Frontend: https://local-lift-production.vercel.app

## Deployment Targets

### Railway (Backend)

The backend is deployed to Railway with environment-specific configurations:

- **Service Name**: locallift-{environment} (e.g., locallift-production)
- **Health Check Endpoint**: https://locallift-{environment}.up.railway.app/api/health
- **Configuration**: Uses environment variables from GitHub secrets and environment-specific settings

### Vercel (Frontend)

The frontend is deployed to Vercel with environment-specific configurations:

- **Project Name**: Determined by Vercel project ID secrets
- **Environment**: Set based on the target environment
- **API Configuration**: Dynamically updated to point to the correct backend URL
- **Deployment Mode**: Production mode for main branch, preview mode for others

## Monitoring and Reporting

The pipeline includes comprehensive monitoring and reporting:

### Health Checks

After deployment, the pipeline performs health checks to verify the application is working:

```yaml
- name: Wait for deployment and perform health check
  run: |
    echo "Waiting for deployment to complete..."
    sleep 60
    
    # Health check retries
    MAX_RETRIES=10
    RETRY_COUNT=0
    HEALTH_URL="https://locallift-${{ env.DEPLOY_ENV }}.up.railway.app/api/health"
    
    while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
      STATUS=$(curl -s -o /dev/null -w "%{http_code}" $HEALTH_URL || echo "failed")
      
      if [ "$STATUS" == "200" ]; then
        echo "✅ Backend deployment successful!"
        exit 0
      fi
      
      echo "Backend not ready yet (status: $STATUS). Retrying in 15 seconds..."
      sleep 15
      RETRY_COUNT=$((RETRY_COUNT+1))
    done
    
    echo "❌ Backend health check failed after $MAX_RETRIES attempts. Manual verification required."
    curl -v $HEALTH_URL
    exit 1
```

### Deployment Reports

Each deployment generates a report with key information:

```yaml
- name: Create deployment report
  run: |
    mkdir -p reports
    cat > reports/deployment-summary.md << EOF
    # Deployment Report
    
    ## Environment
    Environment: **${{ env.DEPLOY_ENV }}**
    Build ID: **${{ needs.build.outputs.build_id }}**
    Commit: **${{ github.sha }}**
    
    ## URLs
    - Backend: https://locallift-${{ env.DEPLOY_ENV }}.up.railway.app
    - Frontend: https://local-lift-${{ env.DEPLOY_ENV }}.vercel.app
    
    ## Deployment Status
    ✅ Backend: Deployed successfully
    ✅ Frontend: Deployed successfully
    
    ## Notes
    This deployment was triggered by ${{ github.actor }} via ${{ github.event_name }}
    
    ## Timestamp
    Deployed at: $(date -u +'%Y-%m-%d %H:%M:%S UTC')
    EOF
```

### Extended Monitoring

For production deployments, an extended monitoring period is implemented:

```yaml
- name: Monitor deployment
  run: |
    echo "Starting post-deployment monitoring..."
    python tools/monitor_deployment.py \
      --backend-url https://locallift-production.up.railway.app \
      --frontend-url https://local-lift-frontend.vercel.app \
      --duration 300 \
      --interval 15 \
      --output-dir ./monitoring-results
```

## Managing GitHub Secrets

The pipeline requires several GitHub secrets to be configured:

- **RAILWAY_TOKEN**: API token for Railway deployments
- **VERCEL_TOKEN**: API token for Vercel deployments
- **VERCEL_ORG_ID**: Organization ID for Vercel
- **VERCEL_PROJECT_ID_DEV**: Vercel project ID for development environment
- **VERCEL_PROJECT_ID_STAGING**: Vercel project ID for staging environment
- **VERCEL_PROJECT_ID_PROD**: Vercel project ID for production environment

To add or update these secrets:

1. Navigate to your GitHub repository
2. Go to Settings > Secrets and variables > Actions
3. Click "New repository secret" to add each secret
4. Ensure each secret has the correct permission scope for the actions it's used with

## Troubleshooting

Common issues and their solutions:

### Failed Quality Checks

If quality checks fail:

1. Check the GitHub Actions output for specific errors
2. Address linting issues, security vulnerabilities, or null byte problems
3. Run `python tools/pre_deploy_check.py --fix` locally to fix common issues
4. Push the fixes and retry the workflow

### Deployment Failures

If deployment fails:

1. Check if the required secrets are configured correctly
2. Verify that the Railway and Vercel project IDs are correct for the environment
3. Check if there are any service-specific errors in the logs
4. For Railway: Verify the service exists and your token has appropriate permissions
5. For Vercel: Check if the project is correctly configured and accessible

### Health Check Failures

If health checks fail:

1. Check if the backend service is running correctly
2. Verify network connectivity and firewall settings
3. Check if the health endpoint is implemented correctly
4. Review application logs for potential errors
5. Check if environment variables are correctly set

### Manual Workflow Trigger

To manually trigger the workflow:

1. Go to the Actions tab in your GitHub repository
2. Select the "LocalLift CI/CD Pipeline" workflow
3. Click "Run workflow"
4. Select the branch to run on
5. Configure the options:
   - Environment (development, staging, production)
   - Deploy backend (checkbox)
   - Deploy frontend (checkbox)
6. Click "Run workflow"

This allows for targeted deployments of specific components to specific environments, which is useful for hotfixes or partial updates.
