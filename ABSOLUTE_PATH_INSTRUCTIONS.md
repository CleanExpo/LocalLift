# MCP-Powered Deployment Automation - Absolute Path Instructions

It appears you're trying to run the automation scripts from the `C:\WINDOWS\system32` directory, but the scripts are located in your Desktop folder. Here are the correct absolute path instructions:

## Full Path Instructions

### Option 1: Navigate to the correct directory first

```powershell
cd C:\Users\PhillMcGurk\Desktop\LocalLift\deployment-automation
.\run_auto_deployment_fixed.ps1
```

### Option 2: Run directly using full path from any location

```powershell
& "C:\Users\PhillMcGurk\Desktop\LocalLift\deployment-automation\run_auto_deployment_fixed.ps1"
```

### Option 3: For scheduled tasks (admin PowerShell required)

```powershell
& "C:\Users\PhillMcGurk\Desktop\LocalLift\deployment-automation\setup_scheduled_task.ps1"
```

### Option 4: For CI/CD or non-interactive execution

```powershell
& "C:\Users\PhillMcGurk\Desktop\LocalLift\deployment-automation\run_automation_noninteractive.ps1"
```

## Troubleshooting

If you still have issues running the scripts, you might need to set the execution policy:

```powershell
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
& "C:\Users\PhillMcGurk\Desktop\LocalLift\deployment-automation\run_auto_deployment_fixed.ps1"
```

## API Token Storage

Your API tokens are already stored in:
- `C:\Users\PhillMcGurk\Desktop\LocalLift\deployment-automation\.env`

## Configuration Files

The automation has already configured the following files:
- Endpoints: `C:\Users\PhillMcGurk\Desktop\LocalLift\deployment-automation\mcp-env\endpoints.json`
- Environment: `C:\Users\PhillMcGurk\Desktop\LocalLift\deployment-automation\mcp-env\.env`

## Logs

Logs will be stored in:
- `C:\Users\PhillMcGurk\Desktop\LocalLift\deployment-automation\deployment-logs\`
