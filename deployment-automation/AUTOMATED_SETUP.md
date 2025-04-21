# Setting Up Automated Deployment Monitoring

This guide explains how to set up MCP-Powered Deployment Automation to run automatically on a schedule or as part of a CI/CD pipeline.

## Table of Contents
1. [Windows Scheduled Task](#windows-scheduled-task)
2. [Linux Cron Job](#linux-cron-job)
3. [GitHub Actions Integration](#github-actions-integration)
4. [API Tokens Configuration](#api-tokens-configuration)
5. [Monitoring and Notifications](#monitoring-and-notifications)

## Windows Scheduled Task

### Option 1: Using the Setup Script

We've provided a script to automatically create a scheduled task on Windows:

```powershell
# Run as administrator
.\setup_scheduled_task.ps1
```

This script will:
1. Create a scheduled task named "LocalLift Deployment Monitor"
2. Set it to run daily at 8:00 AM
3. Run the non-interactive automation script

### Option 2: Manual Task Creation

1. Open Task Scheduler (search for "Task Scheduler" in Start menu)
2. Click "Create Basic Task..."
3. Name: "LocalLift Deployment Monitor"
4. Trigger: Choose your preferred schedule (Daily recommended)
5. Action: "Start a program"
6. Program/script: `powershell.exe`
7. Arguments: `-ExecutionPolicy Bypass -File "C:\path\to\LocalLift\deployment-automation\run_automation_noninteractive.ps1"`
8. Finish the wizard

## Linux Cron Job

Add a cron job to run the automation script daily:

1. Open the crontab editor:
```bash
crontab -e
```

2. Add the following line to run daily at 8:00 AM:
```
0 8 * * * cd /path/to/LocalLift/deployment-automation && pwsh ./run_automation_noninteractive.ps1 >> /path/to/deployment_automation.log 2>&1
```

3. Save and exit the editor

## GitHub Actions Integration

Create a GitHub Actions workflow to run the automation on a schedule or after pushes:

1. Create a file at `.github/workflows/deployment-monitor.yml`:

```yaml
name: Deployment Monitoring

on:
  schedule:
    - cron: '0 8 * * *'  # Run daily at 8:00 AM UTC
  workflow_dispatch:      # Allow manual trigger

jobs:
  monitor:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v2
        
      - name: Set up PowerShell
        uses: actions/setup-node@v2
        with:
          node-version: '14'
      
      - name: Install PowerShell
        run: |
          wget -q https://packages.microsoft.com/config/ubuntu/20.04/packages-microsoft-prod.deb
          sudo dpkg -i packages-microsoft-prod.deb
          sudo apt-get update
          sudo apt-get install -y powershell
      
      - name: Install Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      
      - name: Install Dependencies
        run: |
          pip install -r deployment-automation/requirements.txt
          npm install -g hyperbrowser-mcp @modelcontextprotocol/fetch-mcp
      
      - name: Run Deployment Monitoring
        run: |
          cd deployment-automation
          pwsh ./run_automation_noninteractive.ps1
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
          VERCEL_TOKEN: ${{ secrets.VERCEL_TOKEN }}
```

2. Add your API tokens as secrets in your GitHub repository

## API Tokens Configuration

For automated runs, you'll need to configure API tokens securely:

### Method 1: Environment Variables

Create a `.env` file in the `deployment-automation` directory:

```
RAILWAY_TOKEN=your_railway_token_here
VERCEL_TOKEN=your_vercel_token_here
```

The scripts will automatically detect and use these environment variables.

### Method 2: Credentials Configuration File

Create a `credentials.json` file in the `deployment-automation/config` directory:

```json
{
  "railway": {
    "token": "your_railway_token_here",
    "project_id": "optional_project_id"
  },
  "vercel": {
    "token": "your_vercel_token_here",
    "team_id": "optional_team_id"
  }
}
```

Make sure to set appropriate permissions to restrict access to this file:

```powershell
# Windows
icacls .\config\credentials.json /inheritance:r /grant:r "$env:USERNAME:(R,W)"

# Linux/macOS
chmod 600 config/credentials.json
```

## Monitoring and Notifications

### Email Notifications

To receive email notifications after automated runs, create a `notification_config.json` file in the `deployment-automation/config` directory:

```json
{
  "email": {
    "enabled": true,
    "smtp_server": "smtp.example.com",
    "smtp_port": 587,
    "username": "your_email@example.com",
    "password": "your_password",
    "recipients": [
      "admin@example.com",
      "devops@example.com"
    ],
    "send_on_success": false,
    "send_on_failure": true
  }
}
```

### Slack/Teams Notifications

For Slack or Microsoft Teams notifications, add the following to your `notification_config.json`:

```json
{
  "slack": {
    "enabled": true,
    "webhook_url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
    "channel": "#deployments",
    "send_on_success": true,
    "send_on_failure": true
  },
  "teams": {
    "enabled": false,
    "webhook_url": "https://outlook.office.com/webhook/YOUR/WEBHOOK/URL"
  }
}
```

### Setting Up the Notification Script

Run the notification setup script:

```powershell
.\setup_notifications.ps1
```

This will:
1. Create the necessary configuration files
2. Install required notification dependencies
3. Test the notification channels

## Advanced: Creating a Windows Service

For more robust automation, you can create a Windows service:

1. Install NSSM (Non-Sucking Service Manager):
```
choco install nssm
```

2. Create the service:
```powershell
nssm install "LocalLift Deployment Monitor" powershell.exe
nssm set "LocalLift Deployment Monitor" AppParameters "-ExecutionPolicy Bypass -File C:\path\to\LocalLift\deployment-automation\run_automation_noninteractive.ps1"
nssm set "LocalLift Deployment Monitor" AppDirectory "C:\path\to\LocalLift\deployment-automation"
nssm set "LocalLift Deployment Monitor" Start SERVICE_AUTO_START
nssm set "LocalLift Deployment Monitor" ObjectName "LocalSystem"
nssm set "LocalLift Deployment Monitor" DisplayName "LocalLift Deployment Monitor"
nssm set "LocalLift Deployment Monitor" Description "Monitors and fixes LocalLift deployment issues automatically"
```

3. Start the service:
```powershell
Start-Service "LocalLift Deployment Monitor"
```

4. Check service status:
```powershell
Get-Service "LocalLift Deployment Monitor"
