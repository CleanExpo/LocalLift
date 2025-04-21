# Example Usage of MCP-Powered Deployment Automation

This document provides concrete examples of how to use the MCP-Powered Deployment Automation tools for common scenarios.

## Basic Usage Scenarios

### Scenario 1: Troubleshooting a Non-responsive Railway Backend

If your Railway backend deployment is not responding, you can use the automation tools to discover working endpoints and fix common issues:

```powershell
# Navigate to your project directory where the deployment-automation is set up
cd /path/to/your/project

# Run the automation tool
.\run_auto_deployment.ps1
```

The tool will:
1. Discover working endpoints by testing multiple variations
2. Fix PORT configuration in main.py if needed
3. Update API endpoints in frontend configuration
4. Generate a comprehensive report of the issues found and fixed

### Scenario 2: Full Deployment Automation with API Tokens

For a completely automated deployment process with API tokens:

```powershell
# Run with API tokens
.\run_auto_deployment.ps1
# When prompted, provide your Railway and Vercel API tokens
```

With valid API tokens, the tool will:
1. Discover working endpoints
2. Fix code issues
3. Redeploy the application to Railway
4. Update Vercel configuration
5. Verify the deployment is working correctly

### Scenario 3: Python-only Usage (Cross-platform)

If you prefer to use Python directly or are on a non-Windows platform:

```bash
# For endpoint discovery only
python src/mcp_endpoint_discovery.py

# For complete automated fixing
python src/auto_deployment_fixer.py --railway-token YOUR_TOKEN --vercel-token YOUR_TOKEN
```

## Railway-specific Examples

### Fixing PORT Configuration Issues

If your Railway deployment shows a 404 error or crashes on startup:

```powershell
# Run the PORT fix specifically
python src/auto_deployment_fixer.py --fix-port-only
```

This will:
1. Check if your main.py properly uses the PORT environment variable
2. Make the necessary corrections if needed
3. Verify the fix was successful

### Updating API Endpoints

If your frontend is trying to connect to the wrong API endpoint:

```powershell
# Run the endpoint discovery
python src/mcp_endpoint_discovery.py

# Apply discovered endpoints to config.js
python src/auto_deployment_fixer.py --update-config-only
```

## Vercel-specific Examples

### Fixing Vercel Integration

If Vercel is not correctly pointing to your Railway backend:

```powershell
# Run with Vercel token only
.\run_auto_deployment.ps1
# When prompted, provide your Vercel API token and leave Railway token blank
```

The tool will:
1. Discover the correct Railway endpoints
2. Update Vercel environment variables to point to the correct backend
3. Trigger a redeployment if needed

## Custom Configuration Examples

### Using a Specific Known Endpoint

If you already know the correct endpoint but need to apply it to all configurations:

```powershell
# Create a custom config.json
$ConfigJson = @{
    "platforms" = @{
        "railway" = @{
            "default_endpoint" = "https://your-known-endpoint.up.railway.app",
            "alternatives" = @()
        }
    }
}
$ConfigJson | ConvertTo-Json -Depth 4 | Set-Content "config.json"

# Run with the custom config
.\run_auto_deployment.ps1
```

### Adding Support for a New Hosting Platform

If you're using a platform other than Railway or Vercel:

1. Create a new platform module in src/platforms/
2. Implement the required interface
3. Register it in src/platforms/__init__.py
4. Add the platform to your config.json

## Troubleshooting

If the automation doesn't work as expected:

1. Check the detailed logs in the deployment-logs directory
2. Review the endpoints.json file in the mcp-env directory
3. Try running individual components to isolate the issue

For example:
```powershell
# Test endpoint discovery only
python src/mcp_endpoint_discovery.py

# Test deployment verification only
python src/auto_deployment_fixer.py --verify-only
```

## Next Steps

After using the automation tools:

1. Review the generated reports in deployment-logs/
2. Test the application manually to ensure everything is working
3. Update your documentation with the working endpoints

For more information, refer to the full documentation in the README.md file.
