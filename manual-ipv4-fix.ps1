# Manual IPv4 Fix for Railway
# This script manually sets the required environment variables in Railway

Write-Host "LocalLift: Manual IPv4 Connection Fix" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan

# Set IPv4 address for Supabase
$ipv4 = "52.0.91.163"
Write-Host "Using IPv4 address: $ipv4" -ForegroundColor Yellow

# Set Railway variables directly
Write-Host "Setting Railway environment variables..." -ForegroundColor Yellow

# Function to set a Railway variable
function Set-RailwayVariable {
    param (
        [string]$key,
        [string]$value
    )
    
    Write-Host "  Setting $key..." -ForegroundColor Gray
    $command = "railway variables set $key=$value"
    
    try {
        Invoke-Expression $command | Out-Null
        Write-Host "    ✓ Success" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "    ✗ Failed: $_" -ForegroundColor Red
        return $false
    }
}

# Make sure we're linked to the correct Railway project
try {
    Write-Host "Linking to Railway project..." -ForegroundColor Yellow
    Invoke-Expression "railway link -p 0e58b112-f5f5-4285-ad1f-f47d1481045b" | Out-Null
    Write-Host "  ✓ Successfully linked to project" -ForegroundColor Green
}
catch {
    Write-Host "  ✗ Failed to link to project: $_" -ForegroundColor Red
    Write-Host "    Please run 'railway login' and try again" -ForegroundColor Yellow
    exit 1
}

# Set variables for IPv4 connection
$success = $true
$success = $success -and (Set-RailwayVariable -key "POSTGRES_CONNECTION_OPTION" -value '"-c AddressFamily=inet"')
$success = $success -and (Set-RailwayVariable -key "SUPABASE_DB_HOST" -value $ipv4)
$success = $success -and (Set-RailwayVariable -key "SUPABASE_DB_PORT" -value "5432")
$success = $success -and (Set-RailwayVariable -key "SUPABASE_DB_USER" -value "postgres")
$success = $success -and (Set-RailwayVariable -key "SUPABASE_DB_PASSWORD" -value "postgres_password")

# Update the DATABASE_URL to use IPv4
$databaseUrl = "postgresql://postgres:postgres_password@$ipv4:5432/postgres?sslmode=require"
$success = $success -and (Set-RailwayVariable -key "DATABASE_URL" -value $databaseUrl)

# Provide feedback
if ($success) {
    Write-Host "`nAll variables set successfully!" -ForegroundColor Green
}
else {
    Write-Host "`nSome variables failed to set." -ForegroundColor Red
}

# Prompt to redeploy
Write-Host "`nWould you like to redeploy the application now? (y/n)" -ForegroundColor Yellow
$response = Read-Host
if ($response -eq "y") {
    Write-Host "Redeploying application..." -ForegroundColor Cyan
    Invoke-Expression "railway up"
    Write-Host "Deployment complete!" -ForegroundColor Green
}
else {
    Write-Host "Skipping redeployment. You can manually deploy using 'railway up' command." -ForegroundColor Yellow
}

Write-Host "`nManual IPv4 connection fix complete!" -ForegroundColor Green
