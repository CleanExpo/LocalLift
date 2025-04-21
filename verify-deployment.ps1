# LocalLift CRM Deployment Verification Script
# This script checks the status of your deployed components and helps verify everything is working

Write-Host "LocalLift CRM Deployment Verification" -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Cyan

# Define endpoints to check
$railwayHealthEndpoint = "https://locallift-production.up.railway.app/health"
$railwayApiEndpoint = "https://locallift-production.up.railway.app/api/version"
$vercelFrontend = "https://local-lift-adjm0ahjv-admin-cleanexpo247s-projects.vercel.app"

# Check Railway backend health
Write-Host "Checking Railway backend health..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri $railwayHealthEndpoint -Method Get -TimeoutSec 10
    if ($response.status -eq "healthy") {
        Write-Host "✅ Backend is healthy!" -ForegroundColor Green
        Write-Host "   Version: $($response.version)" -ForegroundColor Green
    } else {
        Write-Host "❌ Backend reported unhealthy status: $($response.status)" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Failed to connect to backend health endpoint. Error: $_" -ForegroundColor Red
    Write-Host "   This likely means the database connection issue is still not resolved." -ForegroundColor Red
    Write-Host "   Follow the steps in MANUAL_RAILWAY_SUPABASE_FIX.md to resolve this issue." -ForegroundColor Yellow
}

# Check Railway API version
Write-Host "`nChecking Railway API version..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri $railwayApiEndpoint -Method Get -TimeoutSec 10
    Write-Host "✅ API endpoint responsive!" -ForegroundColor Green
    Write-Host "   Version: $($response.version)" -ForegroundColor Green
    Write-Host "   Environment: $($response.environment)" -ForegroundColor Green
    Write-Host "   Build Date: $($response.build_date)" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to connect to API endpoint. Error: $_" -ForegroundColor Red
}

# Check Vercel frontend
Write-Host "`nChecking Vercel frontend..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri $vercelFrontend -Method Get -TimeoutSec 10
    Write-Host "✅ Frontend is accessible!" -ForegroundColor Green
    Write-Host "   Status: $($response.StatusCode) $($response.StatusDescription)" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to connect to frontend. Error: $_" -ForegroundColor Red
}

# Check if all components are working
Write-Host "`nVerifying Supabase database schema..." -ForegroundColor Yellow
Write-Host "This requires manual verification through the Supabase Dashboard:" -ForegroundColor White
Write-Host "1. Log in to Supabase: https://rsooolwhapkkkwbmybdb.supabase.co" -ForegroundColor White
Write-Host "2. Go to Table Editor" -ForegroundColor White
Write-Host "3. Verify that the following tables exist:" -ForegroundColor White
Write-Host "   - user_roles" -ForegroundColor White
Write-Host "   - user_teams" -ForegroundColor White
Write-Host "   - user_profiles" -ForegroundColor White
Write-Host "   - customers" -ForegroundColor White

# Check for superadmin user
Write-Host "`nVerifying SuperAdmin user..." -ForegroundColor Yellow
Write-Host "This requires manual verification through the Supabase Dashboard:" -ForegroundColor White
Write-Host "1. Log in to Supabase: https://rsooolwhapkkkwbmybdb.supabase.co" -ForegroundColor White
Write-Host "2. Go to SQL Editor" -ForegroundColor White
Write-Host "3. Run the following SQL to check for SuperAdmin users:" -ForegroundColor White
Write-Host "   SELECT * FROM public.user_roles WHERE role = 'superadmin';" -ForegroundColor Cyan

# End-to-end test
Write-Host "`nPerforming end-to-end test..." -ForegroundColor Yellow
Write-Host "This requires manual verification:" -ForegroundColor White
Write-Host "1. Visit the frontend: $vercelFrontend/login/" -ForegroundColor White
Write-Host "2. Login with your SuperAdmin account" -ForegroundColor White
Write-Host "3. Navigate through the dashboard to verify functionality" -ForegroundColor White
Write-Host "4. Check that you have access to all admin features" -ForegroundColor White

# Final check
Write-Host "`nChecking Railway environment variables..." -ForegroundColor Yellow
Write-Host "This requires manual verification through the Railway Dashboard:" -ForegroundColor White
Write-Host "1. Log in to Railway Dashboard" -ForegroundColor White
Write-Host "2. Go to your LocalLift service" -ForegroundColor White
Write-Host "3. Navigate to Variables tab" -ForegroundColor White
Write-Host "4. Verify these essential variables are set:" -ForegroundColor White
Write-Host "   - SUPABASE_URL" -ForegroundColor White
Write-Host "   - SUPABASE_SERVICE_ROLE_KEY" -ForegroundColor White
Write-Host "   - FRONTEND_URL" -ForegroundColor White
Write-Host "   - JWT_SECRET" -ForegroundColor White
Write-Host "   - SUPABASE_DB_HOST (for IPv4 connection)" -ForegroundColor White
Write-Host "   - DATABASE_URL (with proper connection string)" -ForegroundColor White

Write-Host "`nDeployment Verification Complete" -ForegroundColor Cyan
Write-Host "===============================" -ForegroundColor Cyan
Write-Host "If all checks passed, your LocalLift CRM system is fully operational." -ForegroundColor Green
Write-Host "If you encountered any issues, refer to the corresponding troubleshooting guide in FINAL_STEPS_MANUAL.md" -ForegroundColor Yellow
