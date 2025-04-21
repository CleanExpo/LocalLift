# Deploy MCP-Powered Deployment Automation and Run in Automation Mode
# This script initializes the repository and runs the automation tool

# Set error action preference to stop on errors
$ErrorActionPreference = "Stop"

# Set colors for better readability
$infoColor = "Cyan"
$successColor = "Green"
$errorColor = "Red"
$highlightColor = "Yellow"

Write-Host "=================================================" -ForegroundColor $infoColor
Write-Host "  MCP-Powered Deployment Automation Deployment   " -ForegroundColor $infoColor
Write-Host "=================================================" -ForegroundColor $infoColor

# Step 1: Initialize the Git repository
Write-Host "`n[STEP 1] Initializing Git Repository..." -ForegroundColor $infoColor

try {
    # Check if Git is installed
    if (-not (Get-Command "git" -ErrorAction SilentlyContinue)) {
        Write-Host "Error: Git is not installed or not in PATH. Please install Git and try again." -ForegroundColor $errorColor
        exit 1
    }

    # Navigate to the repository directory
    $repoDir = $PSScriptRoot
    Write-Host "Repository directory: $repoDir" -ForegroundColor $highlightColor
    
    # Initialize Git repository
    Write-Host "Initializing Git repository..." -ForegroundColor $highlightColor
    git init $repoDir
    
    # Add all files and make initial commit
    Write-Host "Adding files to Git..." -ForegroundColor $highlightColor
    git -C $repoDir add .
    
    Write-Host "Making initial commit..." -ForegroundColor $highlightColor
    git -C $repoDir commit -m "Initial commit of MCP-Powered Deployment Automation"
    
    Write-Host "Git repository initialized successfully!" -ForegroundColor $successColor
}
catch {
    Write-Host "Error initializing Git repository: $_" -ForegroundColor $errorColor
    exit 1
}

# Step 2: Print GitHub repository URL information
$githubUrl = "https://github.com/locallift/deployment-automation"
Write-Host "`n[GITHUB REPOSITORY]" -ForegroundColor $infoColor
Write-Host "This tool is part of the open-source project:" -ForegroundColor $highlightColor
Write-Host $githubUrl -ForegroundColor $successColor
Write-Host "Share this URL on Reddit and other platforms!" -ForegroundColor $highlightColor

# Step 3: Create mcp-env and deployment-logs directories if they don't exist
Write-Host "`n[STEP 3] Setting up environment directories..." -ForegroundColor $infoColor
$mcpEnvDir = Join-Path $repoDir "mcp-env"
$logsDir = Join-Path $repoDir "deployment-logs"

if (-not (Test-Path $mcpEnvDir)) {
    New-Item -ItemType Directory -Path $mcpEnvDir | Out-Null
    Write-Host "Created MCP environment directory: $mcpEnvDir" -ForegroundColor $successColor
}

if (-not (Test-Path $logsDir)) {
    New-Item -ItemType Directory -Path $logsDir | Out-Null
    Write-Host "Created logs directory: $logsDir" -ForegroundColor $successColor
}

# Step 4: Install required Python packages
Write-Host "`n[STEP 4] Installing required Python packages..." -ForegroundColor $infoColor
try {
    $requirementsFile = Join-Path $repoDir "requirements.txt"
    if (Test-Path $requirementsFile) {
        pip install -r $requirementsFile
        Write-Host "Python packages installed successfully!" -ForegroundColor $successColor
    }
    else {
        Write-Host "Requirements file not found. Installing packages individually..." -ForegroundColor $highlightColor
        pip install requests argparse python-dotenv colorama
        Write-Host "Python packages installed successfully!" -ForegroundColor $successColor
    }
}
catch {
    Write-Host "Error installing Python packages: $_" -ForegroundColor $errorColor
    Write-Host "Continuing anyway, but some functionality may be limited." -ForegroundColor $highlightColor
}

# Step 5: Check for and install MCP servers if needed
Write-Host "`n[STEP 5] Checking MCP servers..." -ForegroundColor $infoColor
try {
    # Check for hyperbrowser-mcp
    $hyperbrowserInstalled = $null -ne (Get-Command "hyperbrowser-mcp" -ErrorAction SilentlyContinue)
    if (-not $hyperbrowserInstalled) {
        Write-Host "Installing hyperbrowser-mcp..." -ForegroundColor $highlightColor
        npm install -g hyperbrowser-mcp
        Write-Host "hyperbrowser-mcp installed successfully!" -ForegroundColor $successColor
    }
    else {
        Write-Host "hyperbrowser-mcp is already installed." -ForegroundColor $successColor
    }
    
    # Check for fetch-mcp
    $fetchMcpPath = "$HOME\OneDrive - Disaster Recovery\Documents\Cline\MCP\fetch-mcp\dist\index.js"
    if (-not (Test-Path $fetchMcpPath)) {
        Write-Host "Note: fetch-mcp not found at expected path. Some functionality may be limited." -ForegroundColor $highlightColor
    }
    else {
        Write-Host "fetch-mcp found at expected path." -ForegroundColor $successColor
    }
}
catch {
    Write-Host "Error checking/installing MCP servers: $_" -ForegroundColor $errorColor
    Write-Host "Continuing anyway, but some functionality may be limited." -ForegroundColor $highlightColor
}

# Step 6: Run the automation tool in non-interactive mode
Write-Host "`n[STEP 6] Running deployment automation in automated mode..." -ForegroundColor $infoColor
try {
    $scriptPath = Join-Path $repoDir "run_auto_deployment.ps1"
    
    if (Test-Path $scriptPath) {
        Write-Host "Starting automation tool..." -ForegroundColor $highlightColor
        & $scriptPath -NonInteractive
        
        Write-Host "`nAutomation tool completed!" -ForegroundColor $successColor
    }
    else {
        Write-Host "Error: Automation script not found at $scriptPath" -ForegroundColor $errorColor
        exit 1
    }
}
catch {
    Write-Host "Error running automation tool: $_" -ForegroundColor $errorColor
    exit 1
}

# Step 7: Show final status and instructions
Write-Host "`n=================================================" -ForegroundColor $infoColor
Write-Host "  DEPLOYMENT COMPLETE  " -ForegroundColor $successColor
Write-Host "=================================================" -ForegroundColor $infoColor
Write-Host "`nGitHub Repository: $githubUrl"
Write-Host "`nTo manually run the tool again:"
Write-Host "  .\run_auto_deployment.ps1"
Write-Host "`nTo check detailed logs:"
Write-Host "  Check files in the deployment-logs directory"
Write-Host "`nTo contribute to this project:"
Write-Host "  See CONTRIBUTING.md for guidelines"
Write-Host "`nThank you for using MCP-Powered Deployment Automation!"
Write-Host "=================================================" -ForegroundColor $infoColor
