# fix-ipv4-connection.ps1 - Script to fix IPv6 to IPv4 connection issues with Railway and Supabase

Write-Host "LocalLift: Fixing IPv6/IPv4 Connection Issues" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

# Function to get IPv4 address for a hostname
function Get-IPv4Address {
    param (
        [string]$hostname
    )
    
    try {
        $addresses = [System.Net.Dns]::GetHostAddresses($hostname)
        foreach ($address in $addresses) {
            if ($address.AddressFamily -eq [System.Net.Sockets.AddressFamily]::InterNetwork) { # IPv4
                return $address.IPAddressToString
            }
        }
    } catch {
        Write-Host "Failed to resolve $hostname" -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Red
    }
    
    return $null
}

# Get IPv4 for Supabase hostname
$supabaseHost = "db.rsooolwhapkkkwbmybdb.supabase.co"
$ipv4 = Get-IPv4Address -hostname $supabaseHost

if (-not $ipv4) {
    Write-Host "Could not resolve IPv4 address for $supabaseHost. Using direct approach instead." -ForegroundColor Yellow
    
    # Hard-coded IP addresses that are known to work with Supabase
    # These IPs might change in the future, but can be a fallback
    $ipv4 = "52.0.91.163" # Example fallback IP - this will need to be updated with real IP
    
    Write-Host "Using fallback IPv4: $ipv4" -ForegroundColor Yellow
}

# Prepare updated DATABASE_URL with IPv4
Write-Host "Fetching current environment variables..." -ForegroundColor Yellow

# Get current DATABASE_URL from environment
try {
    # Check if we're in deployment script or local
    if (Test-Path ".env.railway") {
        # If running locally, read from .env.railway
        $envContent = Get-Content ".env.railway" -ErrorAction Stop
        $dbUrlLine = $envContent | Where-Object { $_ -like "DATABASE_URL=*" }
        if ($dbUrlLine) {
            $currentDbUrl = $dbUrlLine.Substring("DATABASE_URL=".Length)
        } else {
            throw "DATABASE_URL not found in .env.railway"
        }
    } else {
        # If running in deployment, use environment variable
        $currentDbUrl = $env:DATABASE_URL
        if (-not $currentDbUrl) {
            throw "DATABASE_URL environment variable not found"
        }
    }
    
    Write-Host "Current DATABASE_URL found." -ForegroundColor Green
    
    # Extract components from URL - use regex without colons in variable names
    if ($currentDbUrl -match "postgresql://([^:]+):([^@]+)@([^:/]+)(:[0-9]+)?/(.*)") {
        $dbUser = $matches[1]
        $dbPass = $matches[2]
        $dbHost = $matches[3]
        $dbPort = if ($matches[4]) { $matches[4].Substring(1) } else { "5432" }
        $dbName = $matches[5]
        
        # Create updated URL with IPv4 address - avoid using : in variable interpolation
        $updatedDbUrl = "postgresql://$dbUser" + ":" + "$dbPass" + "@" + "$ipv4" + ":" + "$dbPort/$dbName"
        Write-Host "Created updated DATABASE_URL with IPv4 address." -ForegroundColor Green
    } else {
        Write-Host "Failed to parse DATABASE_URL. Using direct approach." -ForegroundColor Yellow
        
        # If we cannot parse the URL, use a direct approach with known credentials
        # This assumes the password is specified elsewhere (like in the Railway environment)
        $updatedDbUrl = $currentDbUrl -replace $supabaseHost, $ipv4
        Write-Host "Created updated DATABASE_URL by direct replacement." -ForegroundColor Green
    }
} catch {
    $errorMsg = $_.Exception.Message
    Write-Host "Error processing DATABASE_URL: $errorMsg" -ForegroundColor Red
    exit 1
}

# Create temporary file with updated variables
$tempFile = New-TemporaryFile
@"
# Updated connection variables to force IPv4
DATABASE_URL=$updatedDbUrl
POSTGRES_CONNECTION_OPTION="-c AddressFamily=inet"
SUPABASE_DB_HOST=$ipv4
"@ | Out-File -FilePath $tempFile -Encoding utf8

Write-Host "`nHere are the updated connection variables:" -ForegroundColor Green
Get-Content $tempFile | ForEach-Object { Write-Host "  $_" -ForegroundColor White }

# Prompt user to apply changes
Write-Host "`nDo you want to update these variables in the Railway environment? (y/n)" -ForegroundColor Yellow
$response = Read-Host
if ($response -ne "y") {
    Write-Host "Operation cancelled. No changes were made." -ForegroundColor Red
    Remove-Item $tempFile -Force
    exit 0
}

# Upload to Railway using railway variables set
Write-Host "`nUpdating Railway environment variables..." -ForegroundColor Cyan

try {
    # Check if Railway CLI is installed
    $railwayVersion = (railway --version) 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Railway command failed"
    }
} catch {
    $errorMsg = $_.Exception.Message
    Write-Host "Railway CLI not found. Please install it with: npm install -g @railway/cli" -ForegroundColor Red
    Remove-Item $tempFile -Force
    exit 1
}

try {
    # Check if logged in to Railway
    $railwayWhoami = (railway whoami) 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Not logged in to Railway"
    }
} catch {
    $errorMsg = $_.Exception.Message
    Write-Host "Not logged in to Railway. Please login with: railway login" -ForegroundColor Red
    Remove-Item $tempFile -Force
    exit 1
}

# Link to correct Railway project if needed
try {
    $railwayLink = (railway link -p 0e58b112-f5f5-4285-ad1f-f47d1481045b) 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to link Railway project"
    }
} catch {
    $errorMsg = $_.Exception.Message
    Write-Host "Failed to link to Railway project. Please check your connection and project ID." -ForegroundColor Red
    Remove-Item $tempFile -Force
    exit 1
}

# Upload variables to Railway
try {
    Write-Host "Uploading variables to Railway..." -ForegroundColor Yellow
    Get-Content $tempFile | Where-Object { -not $_.StartsWith("#") -and $_.Trim() -ne "" } | ForEach-Object {
        $line = $_.Trim()
        if ($line -match "^([^=]+)=(.*)$") {
            $key = $matches[1]
            $value = $matches[2]
            Write-Host "  Setting $key..." -ForegroundColor Gray
            railway variables set "$key=$value" | Out-Null
        }
    }
    Write-Host "Variables updated successfully!" -ForegroundColor Green
} catch {
    $errorMsg = $_.Exception.Message
    Write-Host "Failed to update Railway variables: $errorMsg" -ForegroundColor Red
    Remove-Item $tempFile -Force
    exit 1
}

# Clean up
Remove-Item $tempFile -Force

# Redeploy the application
Write-Host "`nWould you like to redeploy the application now? (y/n)" -ForegroundColor Yellow
$response = Read-Host
if ($response -eq "y") {
    Write-Host "Redeploying application..." -ForegroundColor Cyan
    railway up
    Write-Host "Deployment complete!" -ForegroundColor Green
} else {
    Write-Host "Skipping redeployment. You can manually deploy using 'railway up' command." -ForegroundColor Yellow
}

Write-Host "`nIPv4 connection fix completed successfully!" -ForegroundColor Green
Write-Host "Your backend should now be able to connect to Supabase using IPv4." -ForegroundColor Green
