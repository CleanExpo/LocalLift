# Set IPv4 Connection Variables in Railway
# This is a simplified script to set the IPv4 connection variables

# IPv4 address for Supabase
$ipv4 = "52.0.91.163"
Write-Host "Using IPv4 address: $ipv4" -ForegroundColor Yellow

# Link to the Railway project
Write-Host "Linking to Railway project..." -ForegroundColor Yellow
railway link -p 0e58b112-f5f5-4285-ad1f-f47d1481045b

# Set each variable individually
Write-Host "Setting POSTGRES_CONNECTION_OPTION..." -ForegroundColor Gray
railway variables set "POSTGRES_CONNECTION_OPTION=-c AddressFamily=inet"

Write-Host "Setting SUPABASE_DB_HOST..." -ForegroundColor Gray
railway variables set "SUPABASE_DB_HOST=$ipv4"

Write-Host "Setting SUPABASE_DB_PORT..." -ForegroundColor Gray
railway variables set "SUPABASE_DB_PORT=5432"

Write-Host "Setting SUPABASE_DB_USER..." -ForegroundColor Gray
railway variables set "SUPABASE_DB_USER=postgres"

Write-Host "Setting SUPABASE_DB_PASSWORD..." -ForegroundColor Gray
railway variables set "SUPABASE_DB_PASSWORD=postgres_password"

# Update the DATABASE_URL
Write-Host "Setting DATABASE_URL..." -ForegroundColor Gray
$databaseUrl = "postgresql://postgres:postgres_password@$ipv4:5432/postgres?sslmode=require"
railway variables set "DATABASE_URL=$databaseUrl"

Write-Host "All variables set. Would you like to redeploy now? (y/n)" -ForegroundColor Yellow
$response = Read-Host

if ($response -eq "y") {
    Write-Host "Redeploying application..." -ForegroundColor Cyan
    railway up
    Write-Host "Deployment complete!" -ForegroundColor Green
} else {
    Write-Host "Skipping redeployment." -ForegroundColor Yellow
}

Write-Host "IPv4 configuration complete!" -ForegroundColor Green
