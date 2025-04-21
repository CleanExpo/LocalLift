# Run MCP-Powered Deployment Automation
# This script executes the deployment automation process from the repository

# Set error action preference to stop on errors
$ErrorActionPreference = "Stop"

# Clear the screen
Clear-Host

Write-Host "=================================================" -ForegroundColor Cyan
Write-Host "      LocalLift Deployment Automation Launcher    " -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "This script will launch the MCP-Powered Deployment Automation tool"
Write-Host "to automatically fix and verify your deployment."
Write-Host ""
Write-Host "GitHub Repository:" -ForegroundColor Yellow
Write-Host "https://github.com/locallift/deployment-automation" -ForegroundColor Green
Write-Host ""

# Check if the deployment-automation directory exists
$automationDir = Join-Path $PSScriptRoot "deployment-automation"
if (-not (Test-Path $automationDir)) {
    Write-Host "ERROR: Deployment automation directory not found!" -ForegroundColor Red
    Write-Host "Expected path: $automationDir" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please ensure you have the deployment-automation directory in the LocalLift folder." -ForegroundColor Yellow
    exit 1
}

# Check if the deploy_and_run.ps1 script exists
$deployScript = Join-Path $automationDir "deploy_and_run.ps1"
if (-not (Test-Path $deployScript)) {
    Write-Host "ERROR: Deployment script not found!" -ForegroundColor Red
    Write-Host "Expected path: $deployScript" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please ensure the deploy_and_run.ps1 script exists in the deployment-automation directory." -ForegroundColor Yellow
    exit 1
}

# Display confirmation prompt
Write-Host "Do you want to start the deployment automation process?" -ForegroundColor Yellow
$confirmation = Read-Host "Enter 'y' to continue or any other key to exit"

if ($confirmation -ne "y") {
    Write-Host "Exiting without running the deployment automation." -ForegroundColor Yellow
    exit 0
}

# Navigate to the automation directory and run the script
try {
    Write-Host "`nStarting deployment automation..." -ForegroundColor Cyan
    
    # CD into the directory and run the script
    Set-Location $automationDir
    & $deployScript
    
    # Return to the original directory
    Set-Location $PSScriptRoot
    
    Write-Host "`nDeployment automation completed successfully!" -ForegroundColor Green
}
catch {
    Write-Host "ERROR during deployment automation: $_" -ForegroundColor Red
    Write-Host "`nPlease check the logs in the deployment-logs directory for more information." -ForegroundColor Yellow
    
    # Return to the original directory
    Set-Location $PSScriptRoot
    exit 1
}

# Final instructions
Write-Host "`n=================================================" -ForegroundColor Cyan
Write-Host "               NEXT STEPS                        " -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host "`nTo share this tool with others, provide this GitHub repository URL:"
Write-Host "https://github.com/locallift/deployment-automation" -ForegroundColor Green
Write-Host "`nTo run the automation tool again manually:"
Write-Host "cd deployment-automation" -ForegroundColor Yellow
Write-Host ".\run_auto_deployment.ps1" -ForegroundColor Yellow
Write-Host "`nTo check the detailed logs, look in:"
Write-Host "deployment-automation\deployment-logs\" -ForegroundColor Yellow
Write-Host "`nThank you for using MCP-Powered Deployment Automation!"
