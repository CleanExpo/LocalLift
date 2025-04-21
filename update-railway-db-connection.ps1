# Update Railway Database Connection Configuration
# This script updates the Railway environment with the correct database connection string

Write-Host "🔄 Updating Railway Database Connection Configuration..." -ForegroundColor Green

# Set API token - use the one from user input
$RAILWAY_TOKEN = "e2452fb3-a46a-4986-9394-9bc0fe9c6ab1"
$RAILWAY_PROJECT_ID = "0e58b112-f5f5-4285-ad1f-f47d1481045b"

# Set the environment variable for Railway token
$env:RAILWAY_TOKEN = $RAILWAY_TOKEN

# Verify token and check if logged in
try {
    Write-Host "Verifying Railway authentication..." -ForegroundColor Blue
    $loginStatus = railway whoami
    if ($loginStatus -match "Logged in as") {
        Write-Host "✅ Successfully authenticated with Railway" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Not logged in. Logging in now..." -ForegroundColor Yellow
        railway login
    }
} catch {
    Write-Host "⚠️ Railway CLI not authenticated. Logging in now..." -ForegroundColor Yellow
    railway login
}

# Link to the project
Write-Host "Linking to Railway project..." -ForegroundColor Blue
railway link -p $RAILWAY_PROJECT_ID

# Get database connection details from env file
$envFile = Get-Content -Path ".env.railway" -Raw
if ($envFile -match "DATABASE_URL=postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/([^`r`n]+)") {
    $dbUser = $matches[1]
    $dbPassword = $matches[2]
    $dbHost = $matches[3]
    $dbPort = $matches[4]
    $dbName = $matches[5]

    Write-Host "Database connection details extracted from .env.railway" -ForegroundColor Green
    Write-Host "Host: $dbHost" -ForegroundColor Gray
    Write-Host "Database: $dbName" -ForegroundColor Gray
    Write-Host "User: $dbUser" -ForegroundColor Gray
} else {
    Write-Host "❌ Failed to extract database connection details from .env.railway" -ForegroundColor Red
    exit 1
}

# Create a temporary file to set the variables
$tempFile = New-TemporaryFile
$dbConnectionString = "postgresql://${dbUser}:${dbPassword}@${dbHost}:${dbPort}/${dbName}"

# Write the key variables to the file
@"
DATABASE_URL=$dbConnectionString
DB_URL=$dbConnectionString
SUPABASE_URL=https://rsooolwhapkkkwbmybdb.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJzb29vbHdoYXBra2t3Ym15YmRiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDQ3MDg1NDYsImV4cCI6MjA2MDI4NDU0Nn0.hKGvTKiT0c8270__roY4C66P5haZuXwBpbRSvmpYa34
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJzb29vbHdoYXBra2t3Ym15YmRiIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NDcwODU0NiwiZXhwIjoyMDYwMjg0NTQ2fQ.4z9OqyeU9-CHmDtZwA87ymicFEM-U53yzdeTZwc6KdE
SUPABASE_JWT_SECRET=O4Lav0c7w2IvacWLVaON8Dl3Expl6RDlIUiTLjsyF9tJR78RHtwqEMZG6Hh8ZdCqsWkx6arpwNxt75PZ3heRvg==
SUPABASE_PROJECT_ID=rsooolwhapkkkwbmybdb
"@ | Out-File -FilePath $tempFile

# Update environment variables on Railway
try {
    Write-Host "Updating Railway environment variables..." -ForegroundColor Blue
    Get-Content $tempFile | railway variables
    Write-Host "✅ Environment variables updated successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to update environment variables: $_" -ForegroundColor Red
}

# Clean up temporary file
Remove-Item $tempFile -Force

# Restart the service
try {
    Write-Host "Restarting Railway service to apply changes..." -ForegroundColor Blue
    railway service restart
    Write-Host "✅ Service restart initiated" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to restart service: $_" -ForegroundColor Red
}

# Deploy new version to ensure changes are applied
try {
    Write-Host "🚀 Deploying application to apply configuration changes..." -ForegroundColor Blue
    railway up
    Write-Host "✅ Deployment initiated. Check Railway dashboard for progress." -ForegroundColor Green
    Write-Host "🌎 Application will be available at: https://locallift-production.up.railway.app" -ForegroundColor Cyan
} catch {
    Write-Host "❌ Failed to deploy application: $_" -ForegroundColor Red
}

Write-Host "🔄 Database connection update process completed. Check Railway logs for deployment status." -ForegroundColor Green
