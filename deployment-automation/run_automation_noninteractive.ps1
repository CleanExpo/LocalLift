# Run MCP-Powered Deployment Automation in Non-Interactive Mode
# This script executes the deployment automation process without requiring user input

# Set error action preference to stop on errors
$ErrorActionPreference = "Stop"

# Clear the screen
Clear-Host

Write-Host "=================================================" -ForegroundColor Cyan
Write-Host "  MCP-Powered Deployment Automation - Auto Mode  " -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Starting automated deployment in non-interactive mode..."
Write-Host "GitHub Repository: https://github.com/locallift/deployment-automation" -ForegroundColor Green
Write-Host ""

# Create required directories
$mcpEnvDir = "mcp-env"
$logsDir = "deployment-logs"

if (-not (Test-Path $mcpEnvDir)) {
    New-Item -ItemType Directory -Path $mcpEnvDir | Out-Null
    Write-Host "Created MCP environment directory: $mcpEnvDir" -ForegroundColor Green
}

if (-not (Test-Path $logsDir)) {
    New-Item -ItemType Directory -Path $logsDir | Out-Null
    Write-Host "Created logs directory: $logsDir" -ForegroundColor Green
}

# Get timestamp for log file
$Timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$LogFile = "$logsDir\auto-deployment-$Timestamp.log"

# Install dependencies if required
try {
    # Check if required Python packages are installed
    Write-Host "Checking Python dependencies..." -ForegroundColor Yellow
    python -c "import requests" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Installing requests package..." -ForegroundColor Yellow
        pip install requests | Out-Null
    }
    
    python -c "import dotenv" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Installing python-dotenv package..." -ForegroundColor Yellow
        pip install python-dotenv | Out-Null
    }
    
    python -c "import colorama" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Installing colorama package..." -ForegroundColor Yellow
        pip install colorama | Out-Null
    }
    
    Write-Host "Python dependencies verified." -ForegroundColor Green
}
catch {
    Write-Host "Error checking/installing Python dependencies: $_" -ForegroundColor Red
    Write-Host "Continuing anyway, but some functionality may be limited." -ForegroundColor Yellow
}

# Run the main script in non-interactive mode and log the output
try {
    Write-Host "Running endpoint discovery..." -ForegroundColor Cyan
    python src/mcp_endpoint_discovery.py | Tee-Object -FilePath $LogFile -Append
    
    Write-Host "Running deployment fixer..." -ForegroundColor Cyan
    python src/auto_deployment_fixer.py --non-interactive | Tee-Object -FilePath $LogFile -Append
    
    Write-Host "`nDeployment automation completed!" -ForegroundColor Green
    Write-Host "Log file: $LogFile" -ForegroundColor Yellow
}
catch {
    Write-Host "ERROR during automation: $_" -ForegroundColor Red
    Write-Host "Please check the log file: $LogFile" -ForegroundColor Yellow
    exit 1
}

# Final instructions
Write-Host "`n=================================================" -ForegroundColor Cyan
Write-Host "  AUTOMATION COMPLETE  " -ForegroundColor Green
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host "`nGitHub Repository: https://github.com/locallift/deployment-automation"
Write-Host "`nTo run again manually:"
Write-Host ".\run_auto_deployment.ps1" -ForegroundColor Yellow
Write-Host "`nTo check logs:"
Write-Host "$LogFile" -ForegroundColor Yellow
Write-Host "`nThank you for using MCP-Powered Deployment Automation!"
