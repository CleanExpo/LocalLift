# Push critical environment variables to Railway
# This script updates the Railway project with the correct Supabase configuration

param (
    [string]$ApiToken = "e2452fb3-a46a-4986-9394-9bc0fe9c6ab1",
    [string]$ProjectId = "0e58b112-f5f5-4285-ad1f-f47d1481045b"
)

Write-Host "🚂 Pushing critical environment variables to Railway project..." -ForegroundColor Green

# Function to check if Railway CLI is installed
function Test-RailwayCLI {
    try {
        $null = Get-Command railway -ErrorAction Stop
        return $true
    } catch {
        return $false
    }
}

# Install Railway CLI if not already installed
if (-not (Test-RailwayCLI)) {
    Write-Host "Installing Railway CLI..." -ForegroundColor Yellow
    npm install -g @railway/cli
}

# Set Railway token
Write-Host "Setting Railway authentication token..." -ForegroundColor Blue
$env:RAILWAY_TOKEN = $ApiToken

# Link to the project
Write-Host "Linking to Railway project..." -ForegroundColor Blue
railway link -p $ProjectId

# Load environment variables from .env.railway file
$envContent = Get-Content -Path ".\.env.railway" -Raw
$envLines = $envContent -split "`r?`n" | Where-Object { $_ -match "^[^#].*=.*" }

# Extract key-value pairs and set them as Railway variables
Write-Host "Setting critical environment variables..." -ForegroundColor Blue
foreach ($line in $envLines) {
    if ($line -match "^([^=]+)=(.*)$") {
        $key = $matches[1].Trim()
        $value = $matches[2].Trim()
        
        # Only update critical Supabase and authentication variables
        if ($key -match "SUPABASE_|SECRET_KEY|API_|ENVIRONMENT") {
            Write-Host "Setting $key..." -ForegroundColor Gray
            railway variables set "$key=$value" --silent
        }
    }
}

Write-Host "Variables updated successfully!" -ForegroundColor Green
Write-Host "Restarting the service to apply changes..." -ForegroundColor Yellow
railway service restart

Write-Host "✅ Deployment configuration updated successfully" -ForegroundColor Green
Write-Host "You can now deploy with: railway up" -ForegroundColor Cyan
