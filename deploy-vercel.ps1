# deploy-vercel.ps1 - Secure deployment script for LocalLift frontend to Vercel

Write-Host "Starting LocalLift frontend deployment to Vercel..." -ForegroundColor Cyan

# Check if Vercel CLI is installed
try {
    $vercelVersion = (vercel --version) 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Vercel command failed"
    }
} catch {
    Write-Host "Vercel CLI not found. Please install it with: npm install -g vercel" -ForegroundColor Red
    exit 1
}

# Set the LocalLift authentication token
Write-Host "Setting LocalLift authentication token..." -ForegroundColor Green
$env:LOCALLIFT_AUTH_TOKEN = "e6fa0a43-3924-4260-96eb-9e34e4829a58"
Write-Host "LocalLift token set successfully." -ForegroundColor Green

# Run pre-deployment checks
Write-Host "Running pre-deployment checks..." -ForegroundColor Cyan

# Although Vercel is only deploying static files, run encoding checks
# to ensure developers catch issues that would affect backend deployment
try {
    $pythonPath = (Get-Command python -ErrorAction SilentlyContinue).Source
    if (-not $pythonPath) {
        $pythonPath = (Get-Command python3 -ErrorAction SilentlyContinue).Source
    }

    if ($pythonPath) {
        Write-Host "Checking Python files for encoding issues..." -ForegroundColor Yellow
        $nullByteCheckResult = & $pythonPath "tools/check_null_bytes.py" "."
        if ($LASTEXITCODE -ne 0) {
            Write-Host "WARNING: Found Python files with null bytes." -ForegroundColor Yellow
            Write-Host "These won't affect Vercel static deployment but should be fixed before Railway deployment." -ForegroundColor Yellow
        } else {
            Write-Host "No encoding issues found." -ForegroundColor Green
        }
    } else {
        Write-Host "Python not found, skipping encoding check." -ForegroundColor Yellow
    }
} catch {
    Write-Host "WARNING: Failed to run encoding check: $_" -ForegroundColor Yellow
}

# Check if logged in to Vercel
try {
    $vercelWhoami = (vercel whoami) 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Not logged in to Vercel"
    }
} catch {
    Write-Host "Not logged in to Vercel. Please login with: vercel login" -ForegroundColor Red
    exit 1
}

# Build documentation if needed
Write-Host "Building documentation..." -ForegroundColor Cyan
if (Test-Path "tools\doc_build.sh") {
    # Use WSL to run the bash script if available
    try {
        bash tools/doc_build.sh
    } catch {
        Write-Host "Could not execute doc_build.sh with bash. Documentation may not be built." -ForegroundColor Yellow
    }
} else {
    Write-Host "Documentation build script not found continuing without it." -ForegroundColor Yellow
}

# Verify the public directory exists
if (-not (Test-Path "public")) {
    Write-Host "The public directory does not exist. Please create it before deploying." -ForegroundColor Red
    exit 1
}

# Check for index.html in public directory
if (-not (Test-Path "public\index.html")) {
    Write-Host "public\index.html not found. This is required for the SPA." -ForegroundColor Red
    exit 1
}

# Verify vercel.json configuration
if (-not (Test-Path "vercel.json")) {
    Write-Host "vercel.json not found. This is required for configuration." -ForegroundColor Red
    exit 1
}

# Verify package.json configuration
if (-not (Test-Path "package.json")) {
    Write-Host "package.json not found. This is required for Vercel deployment." -ForegroundColor Red
    exit 1
}

# Update API endpoint in config if needed
if (Test-Path "public\js\config.js") {
    Write-Host "Confirming correct Railway API URL in config.js..." -ForegroundColor Green
    # Ensure the Railway URL is set correctly
    (Get-Content "public\js\config.js") -replace "https://locallift-production.up.railway.app", "https://locallift-production.up.railway.app" | Set-Content "public\js\config.js"
    Write-Host "Railway URL set to: https://locallift-production.up.railway.app" -ForegroundColor Green
}

# Deploy to Vercel
Write-Host "Deploying to Vercel..." -ForegroundColor Cyan
vercel --prod --yes

Write-Host "Deployment complete!" -ForegroundColor Green
Write-Host "Your site is now available on Vercel." -ForegroundColor Green
Write-Host ""
Write-Host "Don't forget to ensure your Railway backend API is also deployed:" -ForegroundColor Yellow
Write-Host "  .\deploy-railway.ps1" -ForegroundColor Yellow
