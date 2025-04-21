# LocalLift CRM: Simple Finalize Deployment Script
# This script performs the basic steps to fix the IPv6/IPv4 connection issue

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

# Step 2: Update the .env.railway file with IPv4 connection variables
Write-Host "`nStep 2: Setting environment variables in .env.railway..." -ForegroundColor Yellow

$envFilePath = ".\.env.railway"
$variables = @{
    "POSTGRES_CONNECTION_OPTION" = "-c AddressFamily=inet"
    "SUPABASE_DB_HOST" = "52.0.91.163"
    "SUPABASE_DB_PORT" = "5432"
    "SUPABASE_DB_USER" = "postgres"
    "SUPABASE_DB_PASSWORD" = "Sanctuary2025!"
    "DATABASE_URL" = "postgresql://postgres:Sanctuary2025!@52.0.91.163:5432/postgres?sslmode=require"
}

# Create or clear the file
if (Test-Path $envFilePath) {
    Clear-Content $envFilePath
}
else {
    New-Item $envFilePath -ItemType File | Out-Null
}

# Add each variable to the file
foreach ($key in $variables.Keys) {
    $value = $variables[$key]
    "$key=$value" | Out-File -FilePath $envFilePath -Append
    Write-Host "  ✓ Added $key to .env.railway file" -ForegroundColor Green
}

Write-Host "`nNote: You'll need to update these variables in the Railway dashboard:" -ForegroundColor Yellow
Write-Host "  1. Go to Railway dashboard: https://railway.app/project/0e58b112-f5f5-4285-ad1f-f47d1481045b" -ForegroundColor White
Write-Host "  2. Navigate to your service (humorous-serenity)" -ForegroundColor White
Write-Host "  3. Click on 'Variables' tab" -ForegroundColor White
Write-Host "  4. Add all the variables shown above" -ForegroundColor White
Write-Host "  5. Click 'Save Variables'" -ForegroundColor White
Write-Host "  6. Go to 'Deployments' tab and click 'Deploy'" -ForegroundColor White

# Step 3: Create a superadmin user in Supabase
Write-Host "`nStep 3: Instructions for creating a superadmin user in Supabase:" -ForegroundColor Yellow
Write-Host "  1. Go to Supabase SQL Editor" -ForegroundColor White
Write-Host "  2. Run this query to generate a UUID:" -ForegroundColor White
Write-Host "     SELECT uuid_generate_v4();" -ForegroundColor Gray
Write-Host "  3. Run this query to create a superadmin (replace with your UUID):" -ForegroundColor White
Write-Host "     INSERT INTO public.user_roles (user_id, role)" -ForegroundColor Gray
Write-Host "     VALUES ('paste-generated-uuid-here', 'superadmin');" -ForegroundColor Gray
Write-Host "  4. Verify with this query:" -ForegroundColor White
Write-Host "     SELECT * FROM public.user_roles WHERE role = 'superadmin';" -ForegroundColor Gray

# Step 4: Final verification
Write-Host "`nStep 4: Final verification steps:" -ForegroundColor Yellow
Write-Host "  1. After deploying to Railway, run the verification script:" -ForegroundColor White
Write-Host "     .\verify-deployment.ps1" -ForegroundColor Gray
Write-Host "  2. Test the backend API endpoint:" -ForegroundColor White
Write-Host "     https://local-lift-production.up.railway.app/health" -ForegroundColor Gray
Write-Host "  3. Test the frontend:" -ForegroundColor White
Write-Host "     https://local-lift-adjm0ahjv-admin-cleanexpo247s-projects.vercel.app" -ForegroundColor Gray

Write-Host "`nDeployment finalization steps complete!" -ForegroundColor Green
