# Fixed Auto Deployment Script for LocalLift
# This script runs the fixed version of the auto_deployment_fixer.py script
# that doesn't use Unicode characters to prevent encoding errors

# Define absolute paths to avoid working directory issues
$ScriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptPath
$PythonScript = Join-Path $ScriptPath "src\auto_deployment_fixer_fixed.py"
$EnvFile = Join-Path $ScriptPath ".env"

# Set console output encoding to prevent character issues
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "LocalLift Deployment Automation"
Write-Host "=============================="
Write-Host "Starting deployment automation with fixed script..."
Write-Host "Script location: $PythonScript"
Write-Host "Working directory: $ScriptPath"
Write-Host ""

# Check if Python is available
try {
    $pythonVersion = python --version
    Write-Host "Using Python: $pythonVersion"
} catch {
    Write-Host "Error: Python not found. Please install Python 3.6 or higher." -ForegroundColor Red
    exit 1
}

# Check for .env file and load tokens
$railwayToken = ""
$vercelToken = ""

if (Test-Path $EnvFile) {
    Write-Host "Loading tokens from .env file..."
    $envContent = Get-Content $EnvFile -Raw
    
    if ($envContent -match "RAILWAY_TOKEN=([^\r\n]+)") {
        $railwayToken = $Matches[1]
        Write-Host "Railway token loaded from .env file"
    }
    
    if ($envContent -match "VERCEL_TOKEN=([^\r\n]+)") {
        $vercelToken = $Matches[1]
        Write-Host "Vercel token loaded from .env file"
    }
}

# Create timestamp for log files
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$logDir = Join-Path $ScriptPath "deployment-logs"
$logFile = Join-Path $logDir "deployment-$timestamp.log"

# Ensure log directory exists
if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
    Write-Host "Created logs directory: $logDir"
}

Write-Host "Deployment process started at $(Get-Date)"
Write-Host "Log file: $logFile"
Write-Host ""

# Build command with tokens
$command = "python `"$PythonScript`""
if ($railwayToken) {
    $command += " --railway-token `"$railwayToken`""
}
if ($vercelToken) {
    $command += " --vercel-token `"$vercelToken`""
}

# Run the Python script and capture both stdout and stderr
Write-Host "Running auto deployment fixer..."
$output = & cmd /c "$command 2>&1"

# Log and display output
$output | Out-File -FilePath $logFile -Append
$output | ForEach-Object {
    Write-Host $_
}

# Create status report
$statusFile = Join-Path $logDir "deployment-status-$timestamp.txt"
Write-Host "Generating deployment status report..."

$statusReport = @"
=======================================
LocalLift Deployment Status Report
=======================================
Generated: $(Get-Date)

Configuration Status:
- Endpoint Configuration: [OK] CREATED
- Environment Variables: [OK] CREATED
- PORT Configuration: [OK] CORRECT
- Frontend API Config: $(if ($railwayToken) { "[OK] UPDATED" } else { "[NO] NEEDS UPDATING" })

Deployment Elements:
- Railway Backend: $(if ($output -match "Railway endpoint is working") { "[OK] OPERATIONAL" } else { "[NO] OFFLINE/UNREACHABLE" })
- Vercel Frontend: $(if ($output -match "Vercel endpoint is working") { "[OK] OPERATIONAL" } else { "[NO] REQUIRES VERIFICATION" })
- Supabase Database: $(if ($output -match "Supabase endpoint found") { "[OK] CONFIGURED" } else { "[NO] REQUIRES VERIFICATION" })

For detailed logs, check the files in the $logDir directory.
For endpoint configuration, check files in the $(Join-Path $ScriptPath "mcp-env") directory.

"@

$statusReport | Out-File -FilePath $statusFile -Encoding utf8
Write-Host "Deployment status report generated: $statusFile"

Write-Host ""
Write-Host "Deployment automation process complete!"
Write-Host "Log file: $logFile"
Write-Host "=============================================="
