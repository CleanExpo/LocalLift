# PowerShell script to commit the additional files we've created

# Navigate to the LocalLift directory first
Push-Location $PSScriptRoot

Write-Host "Adding additional documentation files..." -ForegroundColor Cyan
git add github_secrets_setup.md
git add push-to-github.ps1
git add commit-additional-files.ps1

# Commit changes
Write-Host "Committing additional files..." -ForegroundColor Green
git commit -m "Add GitHub Secrets setup guide and improved push script

This commit includes:
- github_secrets_setup.md: Detailed instructions for setting up GitHub Secrets
- push-to-github.ps1: Script to push local changes to GitHub
- commit-additional-files.ps1: This script for committing additional files"

Write-Host "Additional files committed successfully!" -ForegroundColor Green
Write-Host "Push to GitHub with: git push origin main" -ForegroundColor Yellow

# Return to the original directory
Pop-Location
