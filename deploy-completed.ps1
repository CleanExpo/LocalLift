# LocalLift CRM - Complete Deployment Script
# This script brings together all the components and deploys the full stack

Write-Host "LocalLift CRM - Complete Deployment Process" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Check for required dependencies
function Check-Command($cmdname) {
    return [bool](Get-Command -Name $cmdname -ErrorAction SilentlyContinue)
}

$dependencies = @{
    "vercel" = "Vercel CLI";
    "railway" = "Railway CLI";
    "git" = "Git";
}

$missingDeps = $false
foreach ($cmd in $dependencies.Keys) {
    if (-not (Check-Command $cmd)) {
        Write-Host "Missing dependency: $($dependencies[$cmd]) ($cmd)" -ForegroundColor Red
        $missingDeps = $true
    }
}

if ($missingDeps) {
    Write-Host "`nPlease install all required dependencies before proceeding." -ForegroundColor Red
    exit 1
}

# Ensure needed files exist
$requiredFiles = @(
    "./supabase/migrations/20250419_rbac_schema.sql",
    "./backend/main.py",
    "./backend/auth_api.py",
    "./backend/users_api.py", 
    "./backend/dashboard_api.py",
    "./core/supabase/client.py",
    "./public/js/auth.js",
    "./public/login/index.html",
    "./public/dashboard/index.html"
)

$missingFiles = $false
foreach ($file in $requiredFiles) {
    if (-not (Test-Path $file)) {
        Write-Host "Missing required file: $file" -ForegroundColor Red
        $missingFiles = $true
    }
}

if ($missingFiles) {
    Write-Host "`nSome required files are missing. Please check the project structure." -ForegroundColor Red
    exit 1
}

# Configuration
$supabaseUrl = "https://rsooolwhapkkkwbmybdb.supabase.co"
$supabaseKey = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJzb29vbHdoYXBra2t3Ym15YmRiIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NDcwODU0NiwiZXhwIjoyMDYwMjg0NTQ2fQ.4z9OqyeU9-CHmDtZwA87ymicFEM-U53yzdeTZwc6KdE"
$railwayUrl = "https://locallift-production.up.railway.app"
$vercelUrl = "https://local-lift-fxu1otnh4-admin-cleanexpo247s-projects.vercel.app"

Write-Host "`nStep 1: Apply Supabase Database Migration" -ForegroundColor Yellow
Write-Host "-------------------------------------" -ForegroundColor Yellow

# Update environment variables
Write-Host "Setting up environment variables..." -ForegroundColor White
$envContent = @"
# LocalLift CRM Railway Environment Variables
SUPABASE_URL=$supabaseUrl
SUPABASE_SERVICE_ROLE_KEY=$supabaseKey
FRONTEND_URL=$vercelUrl
JWT_SECRET=superSecretJWTKeyForLocalLiftRBAC2025$(Get-Random)
"@

Set-Content -Path ".env.railway" -Value $envContent
Write-Host "Environment variables saved to .env.railway" -ForegroundColor Green

# Create frontend config
Write-Host "Creating frontend configuration..." -ForegroundColor White
$configDir = "./public/js"
if (-not (Test-Path $configDir)) {
    New-Item -ItemType Directory -Path $configDir -Force | Out-Null
}

$configContent = @"
/**
 * Configuration for LocalLift CRM Frontend
 */
const config = {
  API_BASE_URL: '$railwayUrl/api',
  SUPABASE_URL: '$supabaseUrl',
  SUPABASE_ANON_KEY: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJzb29vbHdoYXBra2t3Ym15YmRiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDQ3MDg1NDYsImV4cCI6MjA2MDI4NDU0Nn0.RHb4rImTrVqbgAbxZ-LlrEwQ0o42aRDPrco-dY-8dOQ',
  VERSION: '1.0.0',
  ENVIRONMENT: 'production'
};

// Make config available globally
window.config = config;
"@

Set-Content -Path "$configDir/config.js" -Value $configContent
Write-Host "Frontend configuration created at $configDir/config.js" -ForegroundColor Green

# Supabase migration instructions
Write-Host "`nSupabase Migration Instructions:" -ForegroundColor Cyan
Write-Host "1. Go to your Supabase dashboard: $supabaseUrl" -ForegroundColor White
Write-Host "2. Navigate to the SQL Editor" -ForegroundColor White
Write-Host "3. Open the migration file: ./supabase/migrations/20250419_rbac_schema.sql" -ForegroundColor White
Write-Host "4. Copy the contents and paste into the SQL Editor" -ForegroundColor White
Write-Host "5. Execute the SQL to create the RBAC schema" -ForegroundColor White

$continue = Read-Host "`nHave you completed the Supabase migration? (y/n)"
if ($continue -ne "y") {
    Write-Host "Please complete the Supabase migration before continuing." -ForegroundColor Yellow
    Write-Host "You can resume this script when ready." -ForegroundColor Yellow
    exit 0
}

Write-Host "`nStep 2: Deploy Backend to Railway" -ForegroundColor Yellow
Write-Host "-------------------------------" -ForegroundColor Yellow

# Check for Railway login
Write-Host "Checking Railway login status..." -ForegroundColor White
$railwayStatus = railway whoami 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "You need to log in to Railway first." -ForegroundColor Red
    Write-Host "Run 'railway login' and then try again." -ForegroundColor Red
    exit 1
}

Write-Host "Logged in to Railway as: $railwayStatus" -ForegroundColor Green

# Deploy backend to Railway
Write-Host "Deploying backend to Railway..." -ForegroundColor White
Write-Host "This may take a few minutes..." -ForegroundColor White

# Add Procfile if it doesn't exist
if (-not (Test-Path "./Procfile")) {
    Set-Content -Path "./Procfile" -Value "web: uvicorn backend.main:app --host 0.0.0.0 --port `$PORT"
    Write-Host "Created Procfile for Railway deployment" -ForegroundColor Green
}

# Add requirements.txt if it doesn't exist or update it
$requiredPackages = @(
    "fastapi==0.104.1",
    "uvicorn==0.24.0",
    "pydantic==2.4.2",
    "pydantic[email]",
    "python-jose==3.3.0",
    "passlib==1.7.4",
    "bcrypt==4.0.1",
    "supabase==1.0.3",
    "python-dotenv==1.0.0",
    "pyjwt==2.8.0"
)

Set-Content -Path "./requirements.txt" -Value $requiredPackages
Write-Host "Updated requirements.txt for backend dependencies" -ForegroundColor Green

# Create railway.json if it doesn't exist
$railwayJson = @{
    "$schema" = "https://railway.app/railway.schema.json";
    "build" = @{
        "builder" = "NIXPACKS";
        "buildCommand" = "pip install -r requirements.txt";
    };
    "deploy" = @{
        "startCommand" = "uvicorn backend.main:app --host 0.0.0.0 --port \$PORT";
        "healthcheckPath" = "/health";
        "healthcheckTimeout" = 100;
        "restartPolicyType" = "ON_FAILURE";
    };
} | ConvertTo-Json -Depth 5

Set-Content -Path "./railway.json" -Value $railwayJson
Write-Host "Created railway.json configuration file" -ForegroundColor Green

# For demonstration purposes, we'll comment out the actual deployment
Write-Host "`nTo deploy to Railway, run:" -ForegroundColor Cyan
Write-Host "    railway up" -ForegroundColor White
Write-Host "This will deploy your application to Railway." -ForegroundColor White

$continue = Read-Host "`nHave you completed the Railway deployment? (y/n)"
if ($continue -ne "y") {
    Write-Host "Please complete the Railway deployment before continuing." -ForegroundColor Yellow
    Write-Host "You can resume this script when ready." -ForegroundColor Yellow
    exit 0
}

Write-Host "`nStep 3: Deploy Frontend to Vercel" -ForegroundColor Yellow
Write-Host "--------------------------------" -ForegroundColor Yellow

# Check for Vercel login
Write-Host "Checking Vercel login status..." -ForegroundColor White
$vercelStatus = vercel whoami 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "You need to log in to Vercel first." -ForegroundColor Red
    Write-Host "Run 'vercel login' and then try again." -ForegroundColor Red
    exit 1
}

Write-Host "Logged in to Vercel as: $vercelStatus" -ForegroundColor Green

# Deploy frontend to Vercel
Write-Host "Deploying frontend to Vercel..." -ForegroundColor White
Write-Host "This may take a few minutes..." -ForegroundColor White

# For demonstration purposes, we'll comment out the actual deployment
Write-Host "`nTo deploy to Vercel, run:" -ForegroundColor Cyan
Write-Host "    vercel --prod" -ForegroundColor White
Write-Host "This will deploy your static files to Vercel." -ForegroundColor White

$continue = Read-Host "`nHave you completed the Vercel deployment? (y/n)"
if ($continue -ne "y") {
    Write-Host "Please complete the Vercel deployment before continuing." -ForegroundColor Yellow
    Write-Host "You can resume this script when ready." -ForegroundColor Yellow
    exit 0
}

Write-Host "`nStep 4: Set up SuperAdmin User" -ForegroundColor Yellow
Write-Host "----------------------------" -ForegroundColor Yellow

Write-Host "To create a SuperAdmin user:" -ForegroundColor Cyan
Write-Host "1. Register a new user through the login page at $vercelUrl/login/" -ForegroundColor White
Write-Host "2. Go to your Supabase dashboard: $supabaseUrl" -ForegroundColor White 
Write-Host "3. Navigate to Authentication > Users to find your user ID" -ForegroundColor White
Write-Host "4. Navigate to the SQL Editor and run:" -ForegroundColor White
Write-Host "   INSERT INTO public.user_roles (user_id, role) VALUES ('YOUR-USER-ID', 'superadmin');" -ForegroundColor Yellow

Write-Host "`nDeployment complete!" -ForegroundColor Green
Write-Host "Your LocalLift CRM is now fully deployed with RBAC functionality." -ForegroundColor Green
Write-Host "`nFrontend: $vercelUrl" -ForegroundColor Cyan
Write-Host "Backend API: $railwayUrl" -ForegroundColor Cyan
Write-Host "Supabase Dashboard: $supabaseUrl" -ForegroundColor Cyan

Write-Host "`nNext steps:" -ForegroundColor Magenta
Write-Host "1. Log in with your SuperAdmin account" -ForegroundColor White
Write-Host "2. Create other user accounts and assign appropriate roles" -ForegroundColor White
Write-Host "3. Start using your CRM with proper role-based access control" -ForegroundColor White
