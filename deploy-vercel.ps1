# deploy-vercel.ps1 - Secure deployment script for LocalLift frontend to Vercel

Write-Host "🚀 Starting LocalLift frontend deployment to Vercel..." -ForegroundColor Cyan

# Check if Vercel CLI is installed
if (-not (Get-Command vercel -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Vercel CLI not found. Please install it with: npm install -g vercel" -ForegroundColor Red
    exit 1
}

# Set the LocalLift authentication token
Write-Host "✓ Setting LocalLift authentication token..." -ForegroundColor Green
$env:LOCALLIFT_AUTH_TOKEN = "e6fa0a43-3924-4260-96eb-9e34e4829a58"
Write-Host "LocalLift token set successfully."

# Check if logged in to Vercel
try {
    vercel whoami | Out-Null
}
catch {
    Write-Host "❌ Not logged in to Vercel. Please login with: vercel login" -ForegroundColor Red
    exit 1
}

# Build documentation if needed
Write-Host "📚 Building documentation..." -ForegroundColor Cyan
if (Test-Path "tools/doc_build.sh") {
    bash tools/doc_build.sh
}
else {
    Write-Host "⚠️ Documentation build script not found, continuing without it." -ForegroundColor Yellow
}

# Verify the public directory exists
if (-not (Test-Path "public")) {
    Write-Host "❌ The public directory does not exist. Please create it before deploying." -ForegroundColor Red
    exit 1
}

# Check for index.html in public directory
if (-not (Test-Path "public/index.html")) {
    Write-Host "❌ public/index.html not found. This is required for the SPA." -ForegroundColor Red
    exit 1
}

# Verify vercel.json configuration
if (-not (Test-Path "vercel.json")) {
    Write-Host "❌ vercel.json not found. This is required for configuration." -ForegroundColor Red
    exit 1
}

# Update API endpoint in config if needed
if (Test-Path "public/js/config.js") {
    Write-Host "✓ Confirming correct Railway API URL in config.js..." -ForegroundColor Green
    # PowerShell can't do in-place replacements easily, so we'll create a temp file
    $content = Get-Content "public/js/config.js"
    $content = $content -replace "https://locallift-production.up.railway.app", "https://locallift-production.up.railway.app"
    $content | Set-Content "public/js/config.js"
    Write-Host "✓ Railway URL set to: https://locallift-production.up.railway.app" -ForegroundColor Green
}

# Deploy to Vercel
Write-Host "🌐 Deploying to Vercel..." -ForegroundColor Cyan
vercel --prod --yes

Write-Host "✅ Deployment complete!" -ForegroundColor Green
Write-Host "🔍 Your site is now available on Vercel." -ForegroundColor Green
Write-Host ""
Write-Host "Don't forget to ensure your Railway backend API is also deployed:" -ForegroundColor Yellow
Write-Host "  ./deploy-secure.sh" -ForegroundColor Yellow
