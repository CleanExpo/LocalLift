# Create GitHub Repository for MCP-Powered Deployment Automation
# This script helps set up a new GitHub repository for sharing the automation tools

# Set error action preference to stop on errors
$ErrorActionPreference = "Stop"

# Set colors for better readability
$infoColor = "Cyan"
$successColor = "Green"
$errorColor = "Red"
$highlightColor = "Yellow"

# Clear the console
Clear-Host

Write-Host "=================================================" -ForegroundColor $infoColor
Write-Host "   GitHub Repository Setup for Deployment Tools  " -ForegroundColor $infoColor
Write-Host "=================================================" -ForegroundColor $infoColor
Write-Host ""

# Check if git is installed
if (-not (Get-Command "git" -ErrorAction SilentlyContinue)) {
    Write-Host "Error: Git is not installed or not in PATH." -ForegroundColor $errorColor
    Write-Host "Please install Git from https://git-scm.com/downloads and try again." -ForegroundColor $highlightColor
    exit 1
}

# Get the script directory (should be the deployment-automation directory)
$scriptDir = $PSScriptRoot

# Check if we're in the deployment-automation directory
if (-not (Test-Path (Join-Path $scriptDir "README.md"))) {
    Write-Host "Error: This script must be run from the deployment-automation directory." -ForegroundColor $errorColor
    Write-Host "Please navigate to that directory and try again." -ForegroundColor $highlightColor
    exit 1
}

# Prompt for GitHub username
Write-Host "Please enter your GitHub information:" -ForegroundColor $infoColor
$githubUsername = Read-Host "GitHub Username"

if ([string]::IsNullOrWhiteSpace($githubUsername)) {
    Write-Host "Error: GitHub username cannot be empty." -ForegroundColor $errorColor
    exit 1
}

# Prompt for repository name
$repoName = Read-Host "Repository Name (default: deployment-automation)"

if ([string]::IsNullOrWhiteSpace($repoName)) {
    $repoName = "deployment-automation"
}

# Confirm repository URL
$repoUrl = "https://github.com/$githubUsername/$repoName"
Write-Host "`nRepository URL will be: $repoUrl" -ForegroundColor $highlightColor
$confirm = Read-Host "Is this correct? (y/n)"

if ($confirm -ne "y") {
    Write-Host "Setup canceled. Please run the script again with the correct information." -ForegroundColor $highlightColor
    exit 0
}

# Create .git directory if it doesn't exist already (initialize repository)
$gitDir = Join-Path $scriptDir ".git"
if (-not (Test-Path $gitDir)) {
    Write-Host "`nInitializing local Git repository..." -ForegroundColor $infoColor
    git init $scriptDir
}

# Update repository URL in documentation files
Write-Host "`nUpdating repository URL in documentation files..." -ForegroundColor $infoColor

$filesToUpdate = @(
    "README.md",
    "CONTRIBUTING.md",
    "INSTALLATION_INSTRUCTIONS.md",
    "AUTOMATED_SETUP.md"
)

foreach ($file in $filesToUpdate) {
    $filePath = Join-Path $scriptDir $file
    if (Test-Path $filePath) {
        $content = Get-Content $filePath -Raw
        
        # Replace any generic GitHub URL pattern with the specific URL
        $content = $content -replace "https:\/\/github\.com\/yourusername\/deployment-automation", $repoUrl
        $content = $content -replace "https:\/\/github\.com\/username\/deployment-automation", $repoUrl
        $content = $content -replace "https:\/\/github\.com\/locallift\/deployment-automation", $repoUrl
        $content = $content -replace "<your-repo-url>", $repoUrl
        
        # For markdown link format [text](url)
        $content = $content -replace '\[([^\]]+)\]\(https:\/\/github\.com\/[^\/]+\/deployment-automation(?:[^\)]*)\)', "[$1]($repoUrl)"
        
        # Update content
        Set-Content -Path $filePath -Value $content
        Write-Host "  ✓ Updated $file" -ForegroundColor $successColor
    }
}

# Create or update .git/config to set the remote URL
git config remote.origin.url $repoUrl

# Add all files to git
Write-Host "`nAdding files to Git..." -ForegroundColor $infoColor
git add --all

# Make initial commit if needed
$hasCommits = git log -1 --oneline 2>$null
if (-not $hasCommits) {
    Write-Host "Creating initial commit..." -ForegroundColor $infoColor
    git commit -m "Initial commit for MCP-Powered Deployment Automation"
}

# Instructions for pushing to GitHub
Write-Host "`n=================================================" -ForegroundColor $infoColor
Write-Host "         GITHUB REPOSITORY SETUP COMPLETE        " -ForegroundColor $successColor
Write-Host "=================================================" -ForegroundColor $infoColor

Write-Host "`nTo complete the setup, follow these steps:" -ForegroundColor $highlightColor
Write-Host "`n1. Create a new repository on GitHub:" -ForegroundColor $infoColor
Write-Host "   Visit: https://github.com/new" -ForegroundColor $highlightColor
Write-Host "   Repository name: $repoName" -ForegroundColor $highlightColor
Write-Host "   Description: MCP-Powered Deployment Automation Tools" -ForegroundColor $highlightColor
Write-Host "   Make it Public or Private as desired" -ForegroundColor $highlightColor
Write-Host "   DO NOT initialize with README, .gitignore, or License" -ForegroundColor $errorColor
Write-Host "   Click 'Create repository'" -ForegroundColor $highlightColor

Write-Host "`n2. Push your local repository to GitHub:" -ForegroundColor $infoColor
Write-Host "   Run these commands:" -ForegroundColor $highlightColor
Write-Host "     git push -u origin main" -ForegroundColor $highlightColor

Write-Host "`nYour repository URL is:" -ForegroundColor $infoColor
Write-Host "  $repoUrl" -ForegroundColor $successColor
Write-Host "`nShare this URL with others to let them use your deployment automation tools!"

# Copy the URL to clipboard if possible
try {
    $repoUrl | Set-Clipboard
    Write-Host "`n(Repository URL has been copied to clipboard)" -ForegroundColor $highlightColor
} catch {
    # Clipboard functionality might not be available on all systems
}
