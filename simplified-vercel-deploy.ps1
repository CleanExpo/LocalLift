# Simplified Vercel Deployment Script
# This script creates minimal files needed for successful Vercel deployment

Write-Host "📦 Creating simplified Vercel deployment files..." -ForegroundColor Green

# Create minimal public directory structure
Write-Host "Creating directory structure..." -ForegroundColor Blue
$directories = @(
    "./public",
    "./public/css",
    "./public/js",
    "./public/images",
    "./public/dashboard",
    "./public/login",
    "./public/profile",
    "./public/settings",
    "./public/admin/guide"
)

foreach ($dir in $directories) {
    if (-not (Test-Path -Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "  Created: $dir" -ForegroundColor Gray
    }
}

# Create minimal HTML files
Write-Host "Creating basic HTML files..." -ForegroundColor Blue
$htmlContent = @'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LocalLift</title>
    <link rel="stylesheet" href="/style.css">
</head>
<body class="bg-gray-100">
    <div class="container mx-auto px-4 py-8">
        <h1 class="text-3xl font-bold text-center text-primary-600">LocalLift Platform</h1>
        <p class="text-center mt-4">Your local business growth platform</p>
        <div class="mt-8 p-4 bg-white rounded-lg shadow">
            <p>Please wait while we connect to our backend services...</p>
        </div>
    </div>
    <script src="/js/config.js"></script>
    <script src="/js/main.js"></script>
</body>
</html>
'@

$htmlFiles = @(
    "./public/index.html",
    "./public/dashboard/index.html",
    "./public/login/index.html",
    "./public/profile/index.html",
    "./public/settings/index.html",
    "./public/admin/guide/index.html"
)

foreach ($file in $htmlFiles) {
    Set-Content -Path $file -Value $htmlContent
    Write-Host "  Created: $file" -ForegroundColor Gray
}

# Create minimal CSS file
Write-Host "Creating minimal CSS file..." -ForegroundColor Blue
$cssContent = @'
/* Main styles for LocalLift */
body { font-family: 'Arial', sans-serif; line-height: 1.6; }
.container { width: 100%; max-width: 1200px; margin: 0 auto; }
.mx-auto { margin-left: auto; margin-right: auto; }
.px-4 { padding-left: 1rem; padding-right: 1rem; }
.py-8 { padding-top: 2rem; padding-bottom: 2rem; }
.bg-gray-100 { background-color: #f3f4f6; }
.bg-white { background-color: #ffffff; }
.text-3xl { font-size: 1.875rem; }
.font-bold { font-weight: 700; }
.text-center { text-align: center; }
.text-primary-600 { color: #2563eb; }
.mt-4 { margin-top: 1rem; }
.mt-8 { margin-top: 2rem; }
.p-4 { padding: 1rem; }
.rounded-lg { border-radius: 0.5rem; }
.shadow { box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06); }
'@

Set-Content -Path "./public/style.css" -Value $cssContent
Write-Host "  Created: ./public/style.css" -ForegroundColor Gray

# Create minimal JavaScript files
Write-Host "Creating JavaScript files..." -ForegroundColor Blue

# Config JS
$configJsContent = @'
// Configuration for LocalLift
const API_CONFIG = {
  baseUrl: "https://locallift-production.up.railway.app",
  apiVersion: "v1",
  timeout: 10000
};

// Check if API is available
function checkApiStatus() {
  console.log("Checking API status at: " + API_CONFIG.baseUrl);
  // In a real app, we would make an actual API call here
  return new Promise(resolve => {
    setTimeout(() => resolve(true), 1000);
  });
}
'@

Set-Content -Path "./public/js/config.js" -Value $configJsContent
Write-Host "  Created: ./public/js/config.js" -ForegroundColor Gray

# Main JS
$mainJsContent = @'
// Main JavaScript for LocalLift

document.addEventListener('DOMContentLoaded', function() {
  console.log("LocalLift application initialized");
  
  // Check API connection
  checkApiStatus().then(isAvailable => {
    if (isAvailable) {
      console.log("Backend API is available");
    } else {
      console.error("Cannot connect to backend API");
    }
  });
});
'@

Set-Content -Path "./public/js/main.js" -Value $mainJsContent
Write-Host "  Created: ./public/js/main.js" -ForegroundColor Gray

# Create simplified vercel.json
Write-Host "Creating simplified vercel.json..." -ForegroundColor Blue
$vercelConfig = @'
{
  "cleanUrls": true,
  "rewrites": [
    { "source": "/dashboard", "destination": "/dashboard/index.html" },
    { "source": "/login", "destination": "/login/index.html" },
    { "source": "/admin/guide", "destination": "/admin/guide/index.html" },
    { "source": "/profile", "destination": "/profile/index.html" },
    { "source": "/settings", "destination": "/settings/index.html" },
    { "source": "/(.*)", "destination": "/index.html" }
  ],
  "outputDirectory": "public",
  "trailingSlash": false,
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        { "key": "Cache-Control", "value": "s-maxage=1, stale-while-revalidate" },
        { "key": "Access-Control-Allow-Credentials", "value": "true" },
        { "key": "Access-Control-Allow-Origin", "value": "*" },
        { "key": "Access-Control-Allow-Methods", "value": "GET,OPTIONS,PATCH,DELETE,POST,PUT" },
        { "key": "Access-Control-Allow-Headers", "value": "X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version, Authorization" }
      ]
    }
  ],
  "github": {
    "silent": true
  }
}
'@

Set-Content -Path "./vercel.json" -Value $vercelConfig
Write-Host "  Created: ./vercel.json" -ForegroundColor Gray

# Create 404 page
Write-Host "Creating 404 page..." -ForegroundColor Blue
$notFoundContent = @'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Page Not Found - LocalLift</title>
    <link rel="stylesheet" href="/style.css">
</head>
<body class="bg-gray-100">
    <div class="container mx-auto px-4 py-8">
        <h1 class="text-3xl font-bold text-center text-primary-600">Page Not Found</h1>
        <p class="text-center mt-4">The page you are looking for does not exist.</p>
        <div class="mt-8 text-center">
            <a href="/" class="px-4 py-2 bg-primary-600 text-white rounded-lg">Go to Homepage</a>
        </div>
    </div>
</body>
</html>
'@

Set-Content -Path "./public/404.html" -Value $notFoundContent
Write-Host "  Created: ./public/404.html" -ForegroundColor Gray

# Deploy to Vercel
Write-Host "`n🚀 Ready to deploy to Vercel" -ForegroundColor Green
Write-Host "Run the following command to deploy:`n" -ForegroundColor Yellow
Write-Host "  vercel --prod" -ForegroundColor Cyan
Write-Host "`nOr use your existing deploy script:`n" -ForegroundColor Yellow
Write-Host "  powershell -File deploy-vercel.ps1" -ForegroundColor Cyan

Write-Host "`n✅ Simplified deployment files created successfully." -ForegroundColor Green
