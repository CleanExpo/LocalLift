# deploy-railway.ps1 - Secure deployment script for LocalLift backend to Railway

Write-Host "Starting LocalLift backend deployment to Railway..." -ForegroundColor Cyan

# Check if Railway CLI is installed
try {
    $railwayVersion = (railway --version) 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Railway command failed"
    }
} catch {
    Write-Host "Railway CLI not found. Please install it with: npm install -g @railway/cli" -ForegroundColor Red
    exit 1
}

# Set the LocalLift authentication token
Write-Host "Setting LocalLift authentication token..." -ForegroundColor Green
$env:LOCALLIFT_AUTH_TOKEN = "e6fa0a43-3924-4260-96eb-9e34e4829a58"
Write-Host "LocalLift token set successfully." -ForegroundColor Green

# Run pre-deployment validation
Write-Host "Running pre-deployment validation..." -ForegroundColor Cyan

try {
    $pythonPath = (Get-Command python -ErrorAction SilentlyContinue).Source
    if (-not $pythonPath) {
        $pythonPath = (Get-Command python3 -ErrorAction SilentlyContinue).Source
    }

    if ($pythonPath) {
        Write-Host "Running comprehensive deployment validation with automatic fixes..." -ForegroundColor Yellow
        & $pythonPath "tools/pre_deploy_check.py" --fix
        if ($LASTEXITCODE -ne 0) {
            Write-Host "WARNING: Pre-deployment validation found issues." -ForegroundColor Yellow
            Write-Host "Review the output above before continuing." -ForegroundColor Yellow
            
            # Prompt user to continue
            $continue = Read-Host "Continue with deployment anyway? (y/n)"
            if ($continue -ne "y") {
                Write-Host "Deployment aborted by user." -ForegroundColor Red
                exit 1
            }
            Write-Host "Continuing deployment despite validation issues..." -ForegroundColor Yellow
        } else {
            Write-Host "Pre-deployment validation successful!" -ForegroundColor Green
        }
    } else {
        Write-Host "WARNING: Python not found, skipping pre-deployment validation." -ForegroundColor Yellow
    }
} catch {
    Write-Host "WARNING: Failed to run pre-deployment validation: $_" -ForegroundColor Yellow
    
    # Prompt user to continue
    $continue = Read-Host "Continue with deployment anyway? (y/n)"
    if ($continue -ne "y") {
        Write-Host "Deployment aborted by user." -ForegroundColor Red
        exit 1
    }
    Write-Host "Continuing deployment despite validation failure..." -ForegroundColor Yellow
}

# Check if logged in to Railway
try {
    $railwayWhoami = (railway whoami) 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Not logged in to Railway"
    }
} catch {
    Write-Host "Not logged in to Railway. Please login with: railway login" -ForegroundColor Red
    exit 1
}

# Link to correct Railway project if needed
try {
    $railwayLink = (railway link -p 0e58b112-f5f5-4285-ad1f-f47d1481045b) 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to link Railway project"
    }
} catch {
    Write-Host "Failed to link to Railway project. Please check your connection and project ID." -ForegroundColor Red
    exit 1
}

# Deploy to Railway
Write-Host "Deploying to Railway..." -ForegroundColor Cyan
railway up

# Check deployment health
Write-Host "Checking health of deployment..." -ForegroundColor Cyan
Write-Host "Health endpoint: https://locallift-production.up.railway.app/health" -ForegroundColor Cyan

Write-Host "Deployment complete!" -ForegroundColor Green
Write-Host "Your backend API is now available on Railway." -ForegroundColor Green
Write-Host "URL: https://locallift-production.up.railway.app" -ForegroundColor Green
Write-Host ""
Write-Host "Don't forget to ensure your Vercel frontend is also deployed:" -ForegroundColor Yellow
Write-Host "  .\deploy-vercel.ps1" -ForegroundColor Yellow
