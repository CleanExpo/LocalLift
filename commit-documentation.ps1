# PowerShell script to commit all deployment documentation and configuration files to git

# Navigate to the LocalLift directory first
Push-Location $PSScriptRoot

# Check if we're in a git repository
if (-not (Test-Path ".git")) {
    Write-Host "Initializing git repository..." -ForegroundColor Cyan
    git init
}

# Add all deployment documentation files
Write-Host "Adding documentation files..." -ForegroundColor Cyan
git add README.md
git add DEPLOYMENT_GUIDE.md
git add GITHUB_ACTIONS_GUIDE.md
git add RAILWAY_DEPLOYMENT.md
git add DEPLOYMENT.md

# Add configuration files
Write-Host "Adding configuration files..." -ForegroundColor Cyan
git add railway.json
git add railway.toml
git add Dockerfile
git add railway_entry.py
git add .env.railway
git add vercel.json
git add public/js/config.js
git add public/config.js

# Add deployment tools
Write-Host "Adding deployment tools..." -ForegroundColor Cyan
git add tools/pre_deploy_check.py
git add tools/check_null_bytes.py
git add tools/fix_null_bytes.py
git add tools/cleanup_temp_files.py
git add tools/monitor_deployment.py

# Add deployment scripts
Write-Host "Adding deployment scripts..." -ForegroundColor Cyan
git add deploy-railway.ps1
git add deploy-vercel.ps1
git add .github/workflows/deploy.yml
git add commit-documentation.sh
git add commit-documentation.ps1

# Commit changes
Write-Host "Committing changes..." -ForegroundColor Green
git commit -m "Add LocalLift deployment system with documentation and tools

This commit includes:
- Comprehensive deployment documentation
- Railway backend configuration
- Vercel frontend configuration
- Deployment validation and monitoring tools
- GitHub Actions CI/CD workflow
- Null byte detection and fixing tools"

Write-Host "Deployment documentation committed successfully!" -ForegroundColor Green
Write-Host "Push to remote repository with: git push origin main" -ForegroundColor Yellow

# Return to the original directory
Pop-Location
