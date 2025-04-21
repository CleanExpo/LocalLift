# Basic Supabase Migration Script for LocalLift CRM
# A simplified script to apply the RBAC migration to Supabase

Write-Host "LocalLift CRM - Basic Supabase Migration" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# Configuration
$migrationFile = "./supabase/migrations/20250419_rbac_schema.sql"
$supabaseUrl = "https://rsooolwhapkkkwbmybdb.supabase.co"
$supabaseKey = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJzb29vbHdoYXBra2t3Ym15YmRiIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NDcwODU0NiwiZXhwIjoyMDYwMjg0NTQ2fQ.4z9OqyeU9-CHmDtZwA87ymicFEM-U53yzdeTZwc6KdE"

# Check migration file
if (-not (Test-Path $migrationFile)) {
    Write-Host "Error: Migration file not found at $migrationFile" -ForegroundColor Red
    exit 1
}

Write-Host "Migration file found. Ready to apply to Supabase." -ForegroundColor Green

# Update environment variables in .env.railway
Write-Host "Updating environment variables..." -ForegroundColor Yellow
$envContent = @"
# LocalLift CRM Railway Environment Variables
SUPABASE_URL=$supabaseUrl
SUPABASE_SERVICE_ROLE_KEY=$supabaseKey
FRONTEND_URL=https://local-lift-fxu1otnh4-admin-cleanexpo247s-projects.vercel.app
JWT_SECRET=superSecretJWTKeyForLocalLiftRBAC2025
"@

Set-Content -Path ".env.railway" -Value $envContent
Write-Host "Environment variables updated in .env.railway" -ForegroundColor Green

# Create frontend config
Write-Host "Creating frontend configuration..." -ForegroundColor Yellow
$configDir = "./public/js"
if (-not (Test-Path $configDir)) {
    New-Item -ItemType Directory -Path $configDir -Force | Out-Null
}

$configContent = @"
/**
 * Configuration for LocalLift CRM Frontend
 */
const config = {
  API_BASE_URL: 'https://locallift-production.up.railway.app/api',
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

# Instructions for database migration
Write-Host "`nTo apply the database migration manually:" -ForegroundColor Cyan
Write-Host "1. Go to your Supabase dashboard: $supabaseUrl" -ForegroundColor White
Write-Host "2. Navigate to the SQL Editor" -ForegroundColor White
Write-Host "3. Copy the contents of $migrationFile" -ForegroundColor White
Write-Host "4. Paste into the SQL Editor and execute" -ForegroundColor White

# Next steps
Write-Host "`nNext steps for deployment:" -ForegroundColor Cyan
Write-Host "1. Deploy the backend to Railway by running:" -ForegroundColor White
Write-Host "   .\deploy-railway.ps1" -ForegroundColor Yellow
Write-Host "2. Redeploy the frontend to Vercel by running:" -ForegroundColor White
Write-Host "   .\deploy-vercel.ps1" -ForegroundColor Yellow
Write-Host "3. Test the connection between frontend and backend" -ForegroundColor White
Write-Host "4. Set up a superadmin user in Supabase by executing this SQL:" -ForegroundColor White
Write-Host "   INSERT INTO public.user_roles (user_id, role) VALUES ('YOUR-USER-ID', 'superadmin');" -ForegroundColor Yellow

Write-Host "`nBasic setup complete!" -ForegroundColor Green
