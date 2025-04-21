# Master Deployment Script for LocalLift CRM RBAC
# This script walks through the final deployment steps

# Function to display section header
function Show-Header {
    param (
        [string]$title
    )
    Write-Host "`n=========================================================================" -ForegroundColor Cyan
    Write-Host " $title" -ForegroundColor Cyan
    Write-Host "=========================================================================" -ForegroundColor Cyan
}

# Function to check if file exists
function Test-FileExists {
    param (
        [string]$path,
        [string]$description
    )
    if (Test-Path $path) {
        Write-Host "✅ $description found at: $path" -ForegroundColor Green
    } else {
        Write-Host "❌ $description not found at: $path" -ForegroundColor Red
        Write-Host "   Please check that the file exists before proceeding." -ForegroundColor Yellow
    }
}

# Start execution
Clear-Host
Show-Header "LocalLift CRM RBAC Final Deployment"
Write-Host "This script will guide you through the final steps needed to complete deployment."
Write-Host "Several steps require manual intervention in the Railway dashboard and Supabase."
Write-Host "Follow each step carefully to ensure proper deployment."

# Step 0: Verify required files exist
Show-Header "STEP 0: Verifying Required Files"
Test-FileExists ".\supabase\migrations\20250419_rbac_schema_fixed.sql" "Fixed RBAC schema SQL file"
Test-FileExists ".\MANUAL_RAILWAY_SUPABASE_FIX.md" "Railway fix guide"
Test-FileExists ".\FINAL_STEPS_MANUAL.md" "Final steps manual"

# Step 1: Fix Railway-Supabase Connection
Show-Header "STEP 1: Fix Railway-Supabase Connection"
Write-Host "This step requires manual intervention in the Railway dashboard."
Write-Host "You need to update environment variables to fix the connection issue."
Write-Host "`nDetailed instructions:" -ForegroundColor Yellow
Write-Host "1. Log in to Railway Dashboard"
Write-Host "2. Navigate to your LocalLift project"
Write-Host "3. Go to Variables tab"
Write-Host "4. Add/Update the following variables (from .env.railway):"
Write-Host "   - SUPABASE_URL"
Write-Host "   - SUPABASE_SERVICE_ROLE_KEY"
Write-Host "   - FRONTEND_URL"
Write-Host "   - JWT_SECRET"
Write-Host "`n5. Add these IPv4 forcing variables:" -ForegroundColor Yellow
Write-Host "   - SUPABASE_DB_HOST=db.rsooolwhapkkkwbmybdb.supabase.co"
Write-Host "   - SUPABASE_DB_PORT=5432"
Write-Host "   - SUPABASE_DB_USER=postgres"
Write-Host "   - SUPABASE_DB_PASSWORD=<your-postgres-password>"
Write-Host "   - DATABASE_URL=postgresql://postgres:<your-postgres-password>@db.rsooolwhapkkkwbmybdb.supabase.co:5432/postgres?sslmode=require"
Write-Host "   - POSTGRES_CONNECTION_OPTION=`"-c AddressFamily=inet`""
Write-Host "`n6. Redeploy your Railway service (via Deployments tab)"
Write-Host "`nFull details in: MANUAL_RAILWAY_SUPABASE_FIX.md" -ForegroundColor Cyan

$response = Read-Host "`nHave you completed Step 1? (y/n)"
if ($response.ToLower() -ne "y") {
    Write-Host "Please complete Step 1 before proceeding." -ForegroundColor Yellow
    Write-Host "You can restart this script after completing the step." -ForegroundColor Yellow
    exit
}

# Step 2: Apply Database Migration to Supabase
Show-Header "STEP 2: Apply Database Migration to Supabase"
Write-Host "This step requires applying the fixed SQL schema to Supabase."
Write-Host "`nDetailed instructions:" -ForegroundColor Yellow
Write-Host "1. Log in to Supabase dashboard: https://rsooolwhapkkkwbmybdb.supabase.co"
Write-Host "2. Navigate to SQL Editor"
Write-Host "3. Create a new query"
Write-Host "4. Copy the content from: supabase\migrations\20250419_rbac_schema_fixed.sql"
Write-Host "5. Paste into the SQL Editor"
Write-Host "6. Execute the SQL"

# Offer to open the SQL file
$response = Read-Host "`nWould you like to open the SQL file to copy its contents? (y/n)"
if ($response.ToLower() -eq "y") {
    Write-Host "Opening SQL file..." -ForegroundColor Yellow
    notepad.exe ".\supabase\migrations\20250419_rbac_schema_fixed.sql"
}

$response = Read-Host "`nHave you completed Step 2? (y/n)"
if ($response.ToLower() -ne "y") {
    Write-Host "Please complete Step 2 before proceeding." -ForegroundColor Yellow
    Write-Host "You can restart this script after completing the step." -ForegroundColor Yellow
    exit
}

# Step 3: Create Master Admin Account
Show-Header "STEP 3: Create Master Admin Account"
Write-Host "This step requires creating your master admin account and assigning the superadmin role."
Write-Host "`nYour Master Admin Credentials:" -ForegroundColor Green
Write-Host "- Username: phill.m@carsi.com.au"
Write-Host "- Password: Sanctuary2025!@#"
Write-Host "`nDetailed instructions:" -ForegroundColor Yellow
Write-Host "1. Visit the frontend: https://local-lift-adjm0ahjv-admin-cleanexpo247s-projects.vercel.app/login/"
Write-Host "2. Register using the credentials above:"
Write-Host "   - Email: phill.m@carsi.com.au"
Write-Host "   - Password: Sanctuary2025!@#"
Write-Host "3. Go to Supabase dashboard"
Write-Host "4. Navigate to Authentication → Users"
Write-Host "5. Find your newly registered user (search for phill.m@carsi.com.au)"
Write-Host "6. Copy the user ID"
Write-Host "7. Execute this SQL in the Supabase SQL Editor:"
Write-Host "   INSERT INTO public.user_roles (user_id, role) VALUES ('YOUR-USER-ID', 'superadmin');" -ForegroundColor Cyan
Write-Host "   (Replace 'YOUR-USER-ID' with the actual user ID you copied)" -ForegroundColor Yellow

# Offer to open the frontend URL
$response = Read-Host "`nWould you like to open the frontend registration page? (y/n)"
if ($response.ToLower() -eq "y") {
    Write-Host "Opening frontend URL in default browser..." -ForegroundColor Yellow
    Start-Process "https://local-lift-adjm0ahjv-admin-cleanexpo247s-projects.vercel.app/login/"
}

Test-FileExists ".\ADMIN_CREDENTIALS_SETUP.md" "Admin Credentials Guide"
if (Test-Path ".\ADMIN_CREDENTIALS_SETUP.md") {
    $response = Read-Host "`nWould you like to open the Admin Credentials Setup guide? (y/n)"
    if ($response.ToLower() -eq "y") {
        Write-Host "Opening Admin Credentials Setup guide..." -ForegroundColor Yellow
        notepad.exe ".\ADMIN_CREDENTIALS_SETUP.md"
    }
}

$response = Read-Host "`nHave you completed Step 3? (y/n)"
if ($response.ToLower() -ne "y") {
    Write-Host "Please complete Step 3 before proceeding." -ForegroundColor Yellow
    Write-Host "You can restart this script after completing the step." -ForegroundColor Yellow
    exit
}

# Step 4: Verify Deployment
Show-Header "STEP 4: Verify Deployment"
Write-Host "Now let's verify the deployment is working correctly."
Write-Host "This will check the health of backend, frontend, and database connection."

$response = Read-Host "`nWould you like to run the deployment verification script? (y/n)"
if ($response.ToLower() -eq "y") {
    Write-Host "Running deployment verification..." -ForegroundColor Yellow
    & .\verify-deployment.ps1
}

# Step 5: Generate Sample Data
Show-Header "STEP 5: Generate Sample Data"
Write-Host "To fully test the UI/UX functionality, it's helpful to generate sample data."
Write-Host "This step will create sample users, customers, interactions, and analytics data."

Test-FileExists ".\generate-sample-data.ps1" "Sample Data Generator"
if (Test-Path ".\generate-sample-data.ps1") {
    $response = Read-Host "`nWould you like to generate sample data for testing? (y/n)"
    if ($response.ToLower() -eq "y") {
        Write-Host "Generating sample data..." -ForegroundColor Yellow
        & .\generate-sample-data.ps1
    }
} else {
    Write-Host "Sample data generator script not found. Skipping this step." -ForegroundColor Yellow
}

# Step 6: UI/UX Verification
Show-Header "STEP 6: UI/UX Verification"
Write-Host "Now let's verify the UI/UX functionality of the deployed site."
Write-Host "`nDetailed instructions:" -ForegroundColor Yellow
Write-Host "1. Visit the frontend: https://local-lift-adjm0ahjv-admin-cleanexpo247s-projects.vercel.app"
Write-Host "2. Test the following user flows:"
Write-Host "   - Registration & Login"
Write-Host "   - Dashboard functionality"
Write-Host "   - User management (with admin account)"
Write-Host "   - Role-based access control (try different roles)"
Write-Host "`nRefer to UI_UX_CHECKLIST.md for comprehensive verification steps."

$response = Read-Host "`nWould you like to open the frontend URL for UI/UX testing? (y/n)"
if ($response.ToLower() -eq "y") {
    Write-Host "Opening frontend URL in default browser..." -ForegroundColor Yellow
    Start-Process "https://local-lift-adjm0ahjv-admin-cleanexpo247s-projects.vercel.app"
}

Test-FileExists ".\UI_UX_CHECKLIST.md" "UI/UX Checklist"
if (Test-Path ".\UI_UX_CHECKLIST.md") {
    $response = Read-Host "`nWould you like to open the UI/UX checklist? (y/n)"
    if ($response.ToLower() -eq "y") {
        Write-Host "Opening UI/UX checklist..." -ForegroundColor Yellow
        notepad.exe ".\UI_UX_CHECKLIST.md"
    }
}

$response = Read-Host "`nHave you completed the UI/UX verification? (y/n)"
if ($response.ToLower() -ne "y") {
    Write-Host "Please complete UI/UX verification before considering the deployment fully complete." -ForegroundColor Yellow
    Write-Host "You can continue, but note that production readiness requires UI/UX verification." -ForegroundColor Yellow
}

# Final Summary
Show-Header "Deployment Status"
Write-Host "If all steps have been completed successfully, your LocalLift CRM should now be fully operational." -ForegroundColor Green
Write-Host "`nImportant URLs:"
Write-Host "- Frontend: https://local-lift-adjm0ahjv-admin-cleanexpo247s-projects.vercel.app"
Write-Host "- Backend: https://locallift-production.up.railway.app"
Write-Host "- Supabase: https://rsooolwhapkkkwbmybdb.supabase.co"
Write-Host "`nIf you encounter any issues, refer to these resources:"
Write-Host "- DEPLOYMENT_README.md - Main deployment documentation"
Write-Host "- FINAL_STEPS_MANUAL.md - Troubleshooting guide"
Write-Host "- UI_UX_CHECKLIST.md - Guide for UI/UX verification"
Write-Host "`nCongratulations on deploying LocalLift CRM with RBAC!" -ForegroundColor Green
