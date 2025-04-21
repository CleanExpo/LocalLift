# LocalLift Deployment Automation Runner
# This script provides a single entry point for all deployment automation tools

# Set error action preference to stop on errors
$ErrorActionPreference = "Stop"

# Create log directory if it doesn't exist
$LogDir = "deployment-logs"
if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir | Out-Null
    Write-Host "Created logs directory: $LogDir" -ForegroundColor Green
}

# Get current timestamp for log files
$Timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$LogFile = "$LogDir\deployment-$Timestamp.log"

# Write to both console and log file
function Write-Log {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    
    $TimeStamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$TimeStamp] $Message" -ForegroundColor $Color
    "[$TimeStamp] $Message" | Out-File -FilePath $LogFile -Append
}

# Function to check if a command exists
function Test-CommandExists {
    param (
        [string]$Command
    )
    
    $exists = $null -ne (Get-Command $Command -ErrorAction SilentlyContinue)
    return $exists
}

function Initialize-Environment {
    Write-Log "Initializing environment..." "Cyan"
    
    # Check for required tools
    if (-not (Test-CommandExists "python")) {
        Write-Log "Python is not installed or not in PATH. Please install Python 3.6+ and try again." "Red"
        exit 1
    }
    
    if (-not (Test-CommandExists "node")) {
        Write-Log "Node.js is not installed or not in PATH. Please install Node.js and try again." "Red"
        exit 1
    }
    
    # Check for required packages
    Write-Log "Checking required packages..." "Cyan"
    
    # Check for Python packages
    try {
        python -c "import requests" 2>$null
        Write-Log "✅ Python requests package is installed" "Green"
    }
    catch {
        Write-Log "Installing requests package..." "Yellow"
        pip install requests | Out-Null
    }
    
    # Check for hyperbrowser-mcp
    if (-not (Test-CommandExists "hyperbrowser-mcp")) {
        Write-Log "Installing hyperbrowser-mcp..." "Yellow"
        npm install -g hyperbrowser-mcp | Out-Null
    }
    else {
        Write-Log "✅ hyperbrowser-mcp is installed" "Green"
    }
    
    # Check for fetch-mcp
    $fetchMcpPath = "$HOME\OneDrive - Disaster Recovery\Documents\Cline\MCP\fetch-mcp\dist\index.js"
    if (-not (Test-Path $fetchMcpPath)) {
        Write-Log "⚠️ fetch-mcp not found at expected path. Will attempt to use global installation." "Yellow"
    }
    else {
        Write-Log "✅ fetch-mcp found at expected path" "Green"
    }
    
    # Create mcp-env directory if it doesn't exist
    $McpEnvDir = "mcp-env"
    if (-not (Test-Path $McpEnvDir)) {
        New-Item -ItemType Directory -Path $McpEnvDir | Out-Null
        Write-Log "Created MCP environment directory: $McpEnvDir" "Green"
    }
    
    Write-Log "Environment initialization complete" "Green"
}

function Run-EndpointDiscovery {
    Write-Log "Running MCP Endpoint Discovery..." "Cyan"
    
    try {
        python src/mcp_endpoint_discovery.py | Tee-Object -FilePath "$LogDir\endpoint-discovery-$Timestamp.log" -Append
        
        if (Test-Path "mcp-env\endpoint_discovery_summary.txt") {
            Write-Log "✅ Endpoint discovery completed successfully" "Green"
            Get-Content "mcp-env\endpoint_discovery_summary.txt" | Select-Object -Skip 3 | Select-Object -First 20 | ForEach-Object {
                Write-Log $_ "Gray"
            }
            return $true
        }
        else {
            Write-Log "❌ Endpoint discovery did not generate a summary file" "Red"
            return $false
        }
    }
    catch {
        Write-Log "❌ Error running endpoint discovery: $_" "Red"
        return $false
    }
}

function Run-AutoDeploymentFixer {
    param (
        [string]$RailwayToken,
        [string]$VercelToken
    )
    
    Write-Log "Running Auto Deployment Fixer..." "Cyan"
    
    $args = @()
    if ($RailwayToken) {
        $args += "--railway-token", $RailwayToken
    }
    
    if ($VercelToken) {
        $args += "--vercel-token", $VercelToken
    }
    
    try {
        python src/auto_deployment_fixer.py @args | Tee-Object -FilePath "$LogDir\auto-fixer-$Timestamp.log" -Append
        
        if (Test-Path "mcp-env\auto_fixer_summary.txt") {
            Write-Log "✅ Auto deployment fixer completed" "Green"
            Get-Content "mcp-env\auto_fixer_summary.txt" | Select-Object -Skip 3 | Select-Object -First 20 | ForEach-Object {
                Write-Log $_ "Gray"
            }
            return $true
        }
        else {
            Write-Log "⚠️ Auto deployment fixer did not generate a summary file" "Yellow"
            return $false
        }
    }
    catch {
        Write-Log "❌ Error running auto deployment fixer: $_" "Red"
        return $false
    }
}

function Test-Deployment {
    Write-Log "Testing final deployment..." "Cyan"
    
    # Test Railway health endpoint
    $HealthEndpoint = $null
    if (Test-Path "mcp-env\.env") {
        $EnvContent = Get-Content "mcp-env\.env"
        $HealthEndpoint = ($EnvContent | Where-Object { $_ -like "HEALTH_ENDPOINT=*" }) -replace "HEALTH_ENDPOINT=", ""
    }
    
    if (-not $HealthEndpoint) {
        Write-Log "⚠️ Could not find health endpoint in configuration" "Yellow"
        return $false
    }
    
    try {
        Write-Log "Testing health endpoint: $HealthEndpoint" "Cyan"
        
        # Use Invoke-WebRequest to test the endpoint
        $Response = Invoke-WebRequest -Uri $HealthEndpoint -Method GET -TimeoutSec 10 -UseBasicParsing
        
        if ($Response.StatusCode -eq 200) {
            Write-Log "✅ Health endpoint is working! Status: 200" "Green"
            return $true
        }
        else {
            Write-Log "❌ Health endpoint returned status: $($Response.StatusCode)" "Red"
            return $false
        }
    }
    catch {
        Write-Log "❌ Error testing health endpoint: $_" "Red"
        return $false
    }
}

function Show-DeploymentStatus {
    Write-Log "Generating deployment status report..." "Cyan"
    
    # Check for configuration files
    $EndpointsJsonExists = Test-Path "mcp-env\endpoints.json"
    $EnvFileExists = Test-Path "mcp-env\.env"
    $SummaryExists = Test-Path "mcp-env\auto_fixer_summary.txt" -or (Test-Path "mcp-env\endpoint_discovery_summary.txt")
    
    # Check if Railway PORT is correctly configured
    $PortConfigured = $false
    if (Test-Path "main.py") {
        $MainPy = Get-Content "main.py" -Raw
        $PortConfigured = $MainPy -match "os\.environ\.get\('PORT'"
    }
    
    # Check if config.js has API endpoint
    $ConfigJsUpdated = $false
    if (Test-Path "public\js\config.js") {
        $ConfigJs = Get-Content "public\js\config.js" -Raw
        $ConfigJsUpdated = $ConfigJs -match "API_BASE_URL\s*="
    }
    
    # Create status report
    $Report = @"
=======================================
LocalLift Deployment Status Report
=======================================
Generated: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

Configuration Status:
- Endpoint Configuration: $(if ($EndpointsJsonExists) { "✅ CREATED" } else { "❌ MISSING" })
- Environment Variables: $(if ($EnvFileExists) { "✅ CREATED" } else { "❌ MISSING" })
- PORT Configuration: $(if ($PortConfigured) { "✅ CORRECT" } else { "❌ NEEDS FIXING" })
- Frontend API Config: $(if ($ConfigJsUpdated) { "✅ UPDATED" } else { "❌ NEEDS UPDATING" })

Deployment Elements:
- Railway Backend: $(if (Test-Deployment) { "✅ ONLINE" } else { "❌ OFFLINE/UNREACHABLE" })
- Vercel Frontend: $(if ($SummaryExists -and (Get-Content "mcp-env\*summary.txt" -Raw) -match "vercel.*✅") { "✅ ACCESSIBLE" } else { "⚠️ REQUIRES VERIFICATION" })
- Supabase Database: $(if ($SummaryExists -and (Get-Content "mcp-env\*summary.txt" -Raw) -match "database.*✅") { "✅ CONNECTED" } else { "⚠️ REQUIRES VERIFICATION" })

For detailed logs, check the files in the $LogDir directory.
For endpoint configuration, check files in the mcp-env directory.

"@
    
    $ReportFile = "$LogDir\deployment-status-$Timestamp.txt"
    $Report | Out-File -FilePath $ReportFile
    
    Write-Log "Deployment status report generated: $ReportFile" "Green"
    $Report -split "`n" | ForEach-Object {
        Write-Log $_ "White"
    }
}

# Main execution
Clear-Host
Write-Log "==============================================" "Cyan"
Write-Log "   LocalLift Automated Deployment Runner     " "Cyan"
Write-Log "==============================================" "Cyan"
Write-Log "Starting deployment automation process at $(Get-Date)" "White"

# Initialize environment
Initialize-Environment

# Prompt for API tokens if in interactive mode
$RailwayToken = $null
$VercelToken = $null

Write-Log "Do you want to provide API tokens for full automation?" "Yellow"
$ProvideTokens = Read-Host "Provide API tokens? (y/n)"

if ($ProvideTokens -eq 'y') {
    Write-Log "API tokens will allow automatic deployment to Railway and configuration of Vercel" "Gray"
    
    $RailwayToken = Read-Host "Railway API token (leave blank to skip)"
    $VercelToken = Read-Host "Vercel API token (leave blank to skip)"
    
    if ($RailwayToken) {
        Write-Log "Railway API token provided" "Green"
    }
    
    if ($VercelToken) {
        Write-Log "Vercel API token provided" "Green"
    }
}

# Run endpoint discovery
$EndpointDiscoverySuccess = Run-EndpointDiscovery

# Run auto deployment fixer if endpoint discovery was successful
if ($EndpointDiscoverySuccess) {
    $FixerSuccess = Run-AutoDeploymentFixer -RailwayToken $RailwayToken -VercelToken $VercelToken
}
else {
    Write-Log "⚠️ Skipping auto deployment fixer due to endpoint discovery failure" "Yellow"
    $FixerSuccess = $false
}

# Generate final status report
Show-DeploymentStatus

Write-Log "Deployment automation process complete!" "Cyan"
Write-Log "Log file: $LogFile" "White"
Write-Log "==============================================" "Cyan"
