# commit-deploy-changes.ps1 - Commit and push deployment configuration changes

Write-Host "🔍 Checking Git status..." -ForegroundColor Cyan
git status

Write-Host ""
Write-Host "🚀 Adding deployment configuration files..." -ForegroundColor Cyan

# Add all the new deployment files
git add railway.toml
git add package.json
git add vercel.json
git add deploy-secure.sh
git add deploy-vercel.sh
git add deploy-vercel.ps1
git add prepare-vercel-deploy.sh
git add prepare-vercel-deploy.ps1
git add DEPLOYMENT.md
git add RAILWAY_DEPLOYMENT.md
git add commit-deploy-changes.sh
git add commit-deploy-changes.ps1

Write-Host ""
Write-Host "✓ Files staged for commit. Current changes:" -ForegroundColor Green
git status

Write-Host ""
Write-Host "📝 Committing changes..." -ForegroundColor Cyan
git commit -m "Add comprehensive deployment configuration for Railway and Vercel"

Write-Host ""
Write-Host "⬆️ Pushing changes to remote repository..." -ForegroundColor Cyan
git push

Write-Host ""
Write-Host "✅ Changes committed and pushed successfully!" -ForegroundColor Green
Write-Host "The LocalLift deployment configuration is now ready for use." -ForegroundColor Green
