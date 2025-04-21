# LocalLift CRM: Finalize Deployment Script
# This script performs the final steps to fix the IPv6/IPv4 connection issue and deploy

Write-Host "LocalLift CRM: Finalizing Deployment" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan

# Step 1: Replace the database connection file with the fixed version
Write-Host "`nStep 1: Replacing database connection file..." -ForegroundColor Yellow
try {
    $connectionFilePath = ".\core\database\connection.py"
    $fixedFilePath = ".\core\database\fixed_connection.py"
    
    # Create a backup of the original file
    Copy-Item -Path $connectionFilePath -Destination "$connectionFilePath.bak" -Force
    Write-Host "  ✓ Original connection file backed up to $connectionFilePath.bak" -ForegroundColor Green
    
    # Replace with the fixed version
    Copy-Item -Path $fixedFilePath -Destination $connectionFilePath -Force
    Write-Host "  ✓ Fixed connection file successfully applied" -ForegroundColor Green
}
catch {
    Write-Host "  ✗ Failed to replace connection file: $_" -ForegroundColor Red
    exit 1
}

# Step 2: Ensure IPv4 connection variables are set in Railway
Write-Host "`nStep 2: Setting Railway environment variables..." -ForegroundColor Yellow

# Function to set Railway environment variables
function Set-RailwayVariable {
    param (
        [string]$key,
        [string]$value
    )
    
    Write-Host "  Setting $key..." -ForegroundColor Gray
    
    # We don't actually set the environment variable locally
    # Just add it to the .env.railway file for reference
    $envFilePath = ".\.env.railway"
    $envLine = "$key=$value"
    
    # Check if line already exists in file
    $found = $false
    if (Test-Path $envFilePath) {
        $content = Get-Content $envFilePath
        foreach ($line in $content) {
            if ($line -match "^$key=") {
                $found = $true
                break
            }
        }
    }
    
    # Add to file if not found
    if (-not $found) {
        if (-not (Test-Path $envFilePath)) {
            New-Item $envFilePath -ItemType File | Out-Null
        }
        Add-Content $envFilePath $envLine
        Write-Host "    ✓ Added to .env.railway file" -ForegroundColor Green
    } else {
        Write-Host "    → Already in .env.railway file" -ForegroundColor Gray
    }
}

# Set the required environment variables
Set-RailwayVariable -key "POSTGRES_CONNECTION_OPTION" -value "-c AddressFamily=inet"
Set-RailwayVariable -key "SUPABASE_DB_HOST" -value "52.0.91.163"
Set-RailwayVariable -key "SUPABASE_DB_PORT" -value "5432"
Set-RailwayVariable -key "SUPABASE_DB_USER" -value "postgres"
Set-RailwayVariable -key "SUPABASE_DB_PASSWORD" -value "Sanctuary2025!"

# Set the DATABASE_URL with IPv4 address
$databaseUrl = "postgresql://postgres:Sanctuary2025!@52.0.91.163:5432/postgres?sslmode=require"
Set-RailwayVariable -key "DATABASE_URL" -value $databaseUrl

Write-Host "`nNote: You'll need to update these variables in the Railway dashboard:" -ForegroundColor Yellow
Write-Host "  1. Go to Railway dashboard: https://railway.app/project/0e58b112-f5f5-4285-ad1f-f47d1481045b" -ForegroundColor White
Write-Host "  2. Navigate to your service (humorous-serenity)" -ForegroundColor White
Write-Host "  3. Click on 'Variables' tab" -ForegroundColor White
Write-Host "  4. Add all the variables shown above" -ForegroundColor White
Write-Host "  5. Click 'Save Variables'" -ForegroundColor White
Write-Host "  6. Go to 'Deployments' tab and click 'Deploy'" -ForegroundColor White

# Step 3: Commit the changes
Write-Host "`nStep 3: Committing changes to Git..." -ForegroundColor Yellow
try {
    git add core/database/connection.py core/database/fixed_connection.py .env.railway
    git commit -m "Fix: Update database connection to force IPv4"
    Write-Host "  ✓ Changes committed successfully" -ForegroundColor Green
}
catch {
    Write-Host "  ✗ Failed to commit changes: $_" -ForegroundColor Red
    Write-Host "    You may need to manually commit the changes" -ForegroundColor Yellow
}

# Step 4: Final instructions
Write-Host "`nFinal Steps:" -ForegroundColor Cyan
Write-Host "1. Push your changes to GitHub" -ForegroundColor White
Write-Host "2. Verify all environment variables in Railway" -ForegroundColor White
Write-Host "3. Deploy the latest version in Railway" -ForegroundColor White
Write-Host "4. Test the deployment with the verify-deployment.ps1 script" -ForegroundColor White
Write-Host "5. Create a superadmin user in Supabase as shown in NEXT_STEPS_AFTER_SCHEMA.md" -ForegroundColor White

Write-Host "`nDeployment finalization complete!" -ForegroundColor Green
