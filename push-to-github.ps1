# PowerShell script to push LocalLift deployment files to GitHub

# Navigate to the LocalLift directory first
Push-Location $PSScriptRoot

Write-Host "Pushing LocalLift deployment files to GitHub..." -ForegroundColor Cyan

# Check if we have a remote named 'origin'
$hasOrigin = git remote | Where-Object { $_ -eq 'origin' }

if (-not $hasOrigin) {
    # Ask for the GitHub repository URL
    $repoUrl = Read-Host "Enter GitHub repository URL (https://github.com/username/repo.git)"
    
    if ([string]::IsNullOrEmpty($repoUrl)) {
        Write-Host "No repository URL provided. Exiting." -ForegroundColor Red
        Pop-Location
        Exit 1
    }
    
    # Add the remote
    Write-Host "Adding GitHub remote as 'origin'..." -ForegroundColor Yellow
    git remote add origin $repoUrl
}

# Check if we're on the 'main' branch
$currentBranch = git branch --show-current

if ($currentBranch -ne "main") {
    # Create and checkout the main branch if it doesn't exist
    Write-Host "Creating and checking out 'main' branch..." -ForegroundColor Yellow
    git checkout -b main
}

# Push to GitHub
Write-Host "Pushing to GitHub..." -ForegroundColor Green

try {
    git push -u origin main
    Write-Host "Successfully pushed to GitHub!" -ForegroundColor Green
    
    # Extract the repository URL for the success message
    $remoteUrl = git remote get-url origin
    if ($remoteUrl -match "github\.com[:/](.*?)(\.git)?$") {
        $repoPath = $Matches[1]
        Write-Host "View your repository at: https://github.com/$repoPath" -ForegroundColor Cyan
    }
} catch {
    Write-Host "Error pushing to GitHub: $_" -ForegroundColor Red
    Write-Host "Tips for troubleshooting:" -ForegroundColor Yellow
    Write-Host "1. Ensure you have the correct permissions for the repository" -ForegroundColor Yellow
    Write-Host "2. Make sure you've authenticated with GitHub (using SSH key or credentials)" -ForegroundColor Yellow
    Write-Host "3. Check if the repository exists on GitHub" -ForegroundColor Yellow
    Write-Host "4. Try manually with: git push -u origin main" -ForegroundColor Yellow
}

# Return to the original directory
Pop-Location
