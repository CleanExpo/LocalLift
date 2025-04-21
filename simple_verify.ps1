# LocalLift CRM - Simple Deployment Verification Script

Write-Host "Starting LocalLift CRM Deployment Verification..." -ForegroundColor Cyan

# Check if Python is available
try {
    python --version
    Write-Host "Python detected successfully." -ForegroundColor Green
}
catch {
    Write-Host "Error: Python is not available. Please install Python 3.6+ and try again." -ForegroundColor Red
    exit 1
}

# Check for required modules
Write-Host "Checking for required Python modules..." -ForegroundColor Cyan
try {
    python -c "import requests"
    Write-Host "Required modules are available." -ForegroundColor Green
}
catch {
    Write-Host "Installing required modules..." -ForegroundColor Yellow
    pip install requests
}

# Run the verification script
Write-Host "Running deployment verification..." -ForegroundColor Cyan
if (Test-Path -Path "verify_deployment.py") {
    python verify_deployment.py --verbose
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Verification completed successfully!" -ForegroundColor Green
        Write-Host "All systems operational." -ForegroundColor Green
    }
    else {
        Write-Host "Verification failed with errors." -ForegroundColor Red
        Write-Host "Please check logs for details." -ForegroundColor Yellow
    }
}
else {
    Write-Host "Error: verify_deployment.py not found!" -ForegroundColor Red
}

Write-Host "Deployment verification process completed." -ForegroundColor Cyan
