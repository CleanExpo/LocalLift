# Setup Scheduled Task for MCP-Powered Deployment Automation
# This script creates a Windows Scheduled Task to run the automation regularly
# Must be run as administrator

# Check if running as administrator
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
$isAdmin = $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "Error: This script must be run as administrator." -ForegroundColor Red
    Write-Host "Please right-click on PowerShell and select 'Run as administrator', then run this script again." -ForegroundColor Yellow
    exit 1
}

# Set colors for better readability
$infoColor = "Cyan"
$successColor = "Green"
$errorColor = "Red"
$highlightColor = "Yellow"

# Clear the console
Clear-Host

Write-Host "=================================================" -ForegroundColor $infoColor
Write-Host "  MCP-Powered Deployment Automation Scheduler    " -ForegroundColor $infoColor
Write-Host "=================================================" -ForegroundColor $infoColor
Write-Host ""

# Get the script directory
$scriptDir = $PSScriptRoot
$nonInteractiveScriptPath = Join-Path $scriptDir "run_automation_noninteractive.ps1"

# Check if the non-interactive script exists
if (-not (Test-Path $nonInteractiveScriptPath)) {
    Write-Host "Error: Could not find the non-interactive script at:" -ForegroundColor $errorColor
    Write-Host $nonInteractiveScriptPath -ForegroundColor $errorColor
    Write-Host "Make sure you're running this script from the deployment-automation directory." -ForegroundColor $highlightColor
    exit 1
}

# Task configuration
$taskName = "LocalLift Deployment Monitor"
$taskDescription = "Automatically monitors and fixes deployment issues for LocalLift using MCP-powered tools"
$taskAuthor = "MCP-Powered Deployment Automation"

# By default, run at 8:00 AM daily
$defaultHour = 8
$defaultMinute = 0

# Prompt for schedule customization
Write-Host "By default, the task will run daily at 8:00 AM." -ForegroundColor $highlightColor
$customSchedule = Read-Host "Do you want to customize the schedule? (y/n)"

if ($customSchedule -eq 'y') {
    $validHour = $false
    while (-not $validHour) {
        try {
            [int]$hour = Read-Host "Enter the hour (0-23)"
            if ($hour -ge 0 -and $hour -le 23) {
                $validHour = $true
                $defaultHour = $hour
            } else {
                Write-Host "Invalid hour. Please enter a number between 0 and 23." -ForegroundColor $errorColor
            }
        } catch {
            Write-Host "Invalid input. Please enter a number." -ForegroundColor $errorColor
        }
    }
    
    $validMinute = $false
    while (-not $validMinute) {
        try {
            [int]$minute = Read-Host "Enter the minute (0-59)"
            if ($minute -ge 0 -and $minute -le 59) {
                $validMinute = $true
                $defaultMinute = $minute
            } else {
                Write-Host "Invalid minute. Please enter a number between 0 and 59." -ForegroundColor $errorColor
            }
        } catch {
            Write-Host "Invalid input. Please enter a number." -ForegroundColor $errorColor
        }
    }
}

# Format the time for display
$taskTime = "{0:D2}:{1:D2}" -f $defaultHour, $defaultMinute
Write-Host "The task will run daily at $taskTime" -ForegroundColor $highlightColor

# Create the task action
$actionExecutable = "powershell.exe"
$actionArguments = "-ExecutionPolicy Bypass -File `"$nonInteractiveScriptPath`""
$action = New-ScheduledTaskAction -Execute $actionExecutable -Argument $actionArguments -WorkingDirectory $scriptDir

# Create the task trigger (daily at specified time)
$trigger = New-ScheduledTaskTrigger -Daily -At "$taskTime"

# Create the task principal (run with highest privileges)
$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest

# Create task settings
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -DontStopOnIdleEnd -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries -MultipleInstances IgnoreNew

# Check if the task already exists
$existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue

if ($existingTask) {
    Write-Host "A task named '$taskName' already exists." -ForegroundColor $highlightColor
    $replaceTask = Read-Host "Do you want to replace it? (y/n)"
    
    if ($replaceTask -eq 'y') {
        # Remove the existing task
        Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
        Write-Host "Existing task removed." -ForegroundColor $successColor
    } else {
        Write-Host "Setup canceled. The existing task was not modified." -ForegroundColor $highlightColor
        exit 0
    }
}

# Create the task
try {
    $task = Register-ScheduledTask -Action $action -Trigger $trigger -Settings $settings -Principal $principal `
        -TaskName $taskName -Description $taskDescription -Force
    
    Write-Host "`nScheduled task '$taskName' created successfully!" -ForegroundColor $successColor
    Write-Host "The task will run daily at $taskTime" -ForegroundColor $successColor
    Write-Host "Task details:" -ForegroundColor $infoColor
    Write-Host "  - Run as: SYSTEM account" -ForegroundColor $infoColor
    Write-Host "  - Command: $actionExecutable $actionArguments" -ForegroundColor $infoColor
    Write-Host "  - Working directory: $scriptDir" -ForegroundColor $infoColor
}
catch {
    Write-Host "Error creating scheduled task: $_" -ForegroundColor $errorColor
    exit 1
}

# Create config directory if it doesn't exist
$configDir = Join-Path $scriptDir "config"
if (-not (Test-Path $configDir)) {
    New-Item -ItemType Directory -Path $configDir | Out-Null
    Write-Host "Created config directory: $configDir" -ForegroundColor $successColor
}

# Prompt for API tokens
Write-Host "`nWould you like to configure API tokens for automated runs?" -ForegroundColor $highlightColor
$configureTokens = Read-Host "Enter 'y' to configure tokens, or any other key to skip"

if ($configureTokens -eq 'y') {
    $envFile = Join-Path $scriptDir ".env"
    
    $railwayToken = Read-Host "Enter your Railway API token (press Enter to skip)"
    $vercelToken = Read-Host "Enter your Vercel API token (press Enter to skip)"
    
    # Save to .env file
    "# API Tokens for MCP-Powered Deployment Automation" | Out-File -FilePath $envFile -Force
    "# Created on $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" | Out-File -FilePath $envFile -Append
    "" | Out-File -FilePath $envFile -Append
    
    if ($railwayToken) {
        "RAILWAY_TOKEN=$railwayToken" | Out-File -FilePath $envFile -Append
        Write-Host "Railway token saved to .env file" -ForegroundColor $successColor
    }
    
    if ($vercelToken) {
        "VERCEL_TOKEN=$vercelToken" | Out-File -FilePath $envFile -Append
        Write-Host "Vercel token saved to .env file" -ForegroundColor $successColor
    }
    
    # Set restricted permissions on the .env file
    $acl = Get-Acl $envFile
    $acl.SetAccessRuleProtection($true, $false)
    $currentUser = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
    $accessRule = New-Object System.Security.AccessControl.FileSystemAccessRule($currentUser, "FullControl", "Allow")
    $acl.AddAccessRule($accessRule)
    $acl | Set-Acl $envFile
    
    Write-Host "Permissions on .env file restricted to current user" -ForegroundColor $successColor
}

# Final instructions
Write-Host "`n=================================================" -ForegroundColor $infoColor
Write-Host "  SCHEDULED TASK SETUP COMPLETE  " -ForegroundColor $successColor
Write-Host "=================================================" -ForegroundColor $infoColor
Write-Host "`nThe deployment automation will now run daily at $taskTime"
Write-Host "`nTo view or modify the task:"
Write-Host "1. Open Task Scheduler" -ForegroundColor $highlightColor
Write-Host "2. Look for the task named '$taskName'" -ForegroundColor $highlightColor
Write-Host "`nTo run the task manually:"
Write-Host "Right-click on the task and select 'Run'" -ForegroundColor $highlightColor
Write-Host "`nTo check logs after automated runs:"
Write-Host "Look in the deployment-logs directory" -ForegroundColor $highlightColor
Write-Host "`nThank you for using MCP-Powered Deployment Automation!"
