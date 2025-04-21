# Railway Configuration Fix Script
# This script logs in to Railway and updates critical environment variables

# Determine the authentication method
Write-Host "Fixing Railway deployment configuration..." -ForegroundColor Green

# Check if Railway CLI is installed
try {
    railway version
    Write-Host "Railway CLI is installed" -ForegroundColor Green
} catch {
    Write-Host "Railway CLI not found. Installing..." -ForegroundColor Yellow
    npm install -g @railway/cli
}

# First, login to Railway
Write-Host "Please login to your Railway account in the browser window that will open..." -ForegroundColor Blue
railway login

# Verify login status
try {
    railway whoami
    Write-Host "Successfully logged in to Railway" -ForegroundColor Green
} catch {
    Write-Host "Failed to login to Railway. Please try again." -ForegroundColor Red
    exit 1
}

# Link to the project
$projectId = "0e58b112-f5f5-4285-ad1f-f47d1481045b"
Write-Host "Linking to Railway project..." -ForegroundColor Blue
railway link -p $projectId

# Load environment variables from .env.railway file
$envContent = Get-Content -Path ".\.env.railway" -Raw
$envLines = $envContent -split "`r?`n" | Where-Object { $_ -match "^[^#].*=.*" }

# Create a temporary JSON file for bulk variable update
$tempVarsFile = [System.IO.Path]::GetTempFileName()
$variablesJson = @{}

# Extract key-value pairs 
Write-Host "Reading critical environment variables..." -ForegroundColor Blue
foreach ($line in $envLines) {
    if ($line -match '^([^=#][^=]*)=(.*)$') {
        $key = $matches[1].Trim()
        $value = $matches[2].Trim()
        
        # Only update critical Supabase and authentication variables
        if ($key -match "SUPABASE_|SECRET_KEY|API_|ENVIRONMENT") {
            $variablesJson[$key] = $value
        }
    }
}

# Convert to JSON and save to temp file
$variablesJson | ConvertTo-Json -Compress | Set-Content -Path $tempVarsFile
Write-Host "Created variables config file" -ForegroundColor Green

# Set the variables in Railway
Write-Host "Updating Railway environment variables..." -ForegroundColor Blue
try {
    cat $tempVarsFile | railway variables 
    Write-Host "Variables updated successfully" -ForegroundColor Green
} catch {
    Write-Host "Failed to update variables" -ForegroundColor Red
}

# Clean up
Remove-Item -Path $tempVarsFile -Force

# Fix database issue - rename SUPABASE_SERVICE_ROLE to SUPABASE_SERVICE_ROLE_KEY if needed
Write-Host "Checking critical variable names..." -ForegroundColor Blue
railway variables set "SUPABASE_SERVICE_ROLE_KEY=$($variablesJson['SUPABASE_SERVICE_ROLE_KEY'])"

# Deploy the application
Write-Host "Deploying LocalLift to Railway..." -ForegroundColor Blue
try {
    # First restart any existing service
    railway service restart
    
    # Then trigger a full deployment
    railway up
    
    Write-Host "Deployment initiated successfully!" -ForegroundColor Green
    Write-Host "Your application will be available at: https://locallift-production.up.railway.app" -ForegroundColor Cyan
} catch {
    Write-Host "Deployment failed" -ForegroundColor Red
}
