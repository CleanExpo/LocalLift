# prepare-vercel-deploy.ps1 - Prepare assets for Vercel deployment

Write-Host "🔧 Preparing assets for Vercel deployment..." -ForegroundColor Cyan

# Create the public/js directory if it doesn't exist
if (-not (Test-Path "public\js")) {
    Write-Host "Creating public\js directory..."
    New-Item -ItemType Directory -Path "public\js" -Force | Out-Null
}

# Copy configuration file to public directory
Write-Host "📝 Copying configuration files to public directory..." -ForegroundColor Cyan
if (Test-Path "static\js\config.js") {
    Copy-Item "static\js\config.js" -Destination "public\js\config.js" -Force
} else {
    Write-Host "❌ Could not find static\js\config.js!" -ForegroundColor Red
    exit 1
}

# Ensure index.html references the correct config.js location
if (Test-Path "public\index.html") {
    Write-Host "✓ Checking index.html for config.js reference..." -ForegroundColor Green
    
    # Read the content of index.html
    $content = Get-Content "public\index.html" -Raw
    
    # Check if index.html includes config.js
    if ($content -match "config.js") {
        # If it references the static path, update it to the public path
        $content = $content -replace 'src="static/js/config.js"', 'src="js/config.js"'
        $content = $content -replace 'src="/static/js/config.js"', 'src="/js/config.js"'
        
        # Write the updated content back to the file
        Set-Content -Path "public\index.html" -Value $content
    } else {
        Write-Host "⚠️ config.js is not referenced in index.html. You may need to add it manually." -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ public\index.html not found. Please ensure it exists before deployment." -ForegroundColor Red
    exit 1
}

# Copy any other necessary static assets
Write-Host "📦 Copying additional static assets..." -ForegroundColor Cyan

# Copy CSS files
if (Test-Path "static\css") {
    if (-not (Test-Path "public\css")) {
        New-Item -ItemType Directory -Path "public\css" -Force | Out-Null
    }
    Copy-Item "static\css\*" -Destination "public\css\" -Recurse -Force
} else {
    Write-Host "No static\css directory found." -ForegroundColor Yellow
}

# Copy image files if they exist
if (Test-Path "static\images") {
    if (-not (Test-Path "public\images")) {
        New-Item -ItemType Directory -Path "public\images" -Force | Out-Null
    }
    Copy-Item "static\images\*" -Destination "public\images\" -Recurse -Force
}

# Copy any additional JS files
if (Test-Path "static\js") {
    Get-ChildItem -Path "static\js" -Filter "*.js" | ForEach-Object {
        Copy-Item $_.FullName -Destination "public\js\" -Force
    }
} else {
    Write-Host "No additional JS files found." -ForegroundColor Yellow
}

Write-Host "✅ Preparation complete! The site is ready for Vercel deployment." -ForegroundColor Green
Write-Host "To deploy, run: .\deploy-vercel.ps1" -ForegroundColor Cyan
