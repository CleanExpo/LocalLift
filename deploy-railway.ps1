# Railway Deployment PowerShell Script for LocalLift
# This script handles the deployment process for Railway on Windows

Write-Host "LocalLift Railway Deployment" -ForegroundColor Cyan
Write-Host "===========================" -ForegroundColor Cyan

# Check if Railway CLI is installed
if (!(Get-Command railway -ErrorAction SilentlyContinue)) {
    Write-Host "Railway CLI not found. Installing..." -ForegroundColor Yellow
    npm i -g @railway/cli
}

# Check if user is logged in to Railway
try {
    railway whoami | Out-Null
    Write-Host "Logged in to Railway." -ForegroundColor Green
} catch {
    Write-Host "Please log in to Railway:" -ForegroundColor Yellow
    railway login
}

# Set the LocalLift authentication token
Write-Host "✓ Setting LocalLift authentication token..." -ForegroundColor Green
$env:LOCALLIFT_AUTH_TOKEN = "e6fa0a43-3924-4260-96eb-9e34e4829a58"
Write-Host "LocalLift token set successfully." -ForegroundColor Green

# Verify railway.json exists
if (-not (Test-Path "railway.json")) {
    Write-Host "❌ railway.json not found. This is required for deployment configuration." -ForegroundColor Red
    exit 1
}

# Commit latest changes
Write-Host "Committing latest changes..." -ForegroundColor Cyan
git add .env.railway railway.json Dockerfile main.py
git commit -m "🚀 Update Railway deployment configuration with multi-region support"

# Push to Railway
Write-Host "Deploying to Railway with advanced configuration..." -ForegroundColor Cyan
railway up

Write-Host ""
Write-Host "Deployment initiated!" -ForegroundColor Green
Write-Host "Note: It may take a few minutes for changes to propagate."
Write-Host "You can check the deployment status in the Railway dashboard."
Write-Host "Once deployed, your API will be available at:"
Write-Host "https://locallift-production.up.railway.app" -ForegroundColor Cyan
Write-Host "Health check endpoint: https://locallift-production.up.railway.app/health" -ForegroundColor Cyan
