# LocalLift CRM - Deployment Verification Script
# This PowerShell script runs the deployment verification and generates a report

Write-Host "Starting LocalLift CRM Deployment Verification..." -ForegroundColor Cyan

# Ensure Python is available
try {
    python --version
    Write-Host "Python detected..." -ForegroundColor Green
}
catch {
    Write-Host "Error: Python is not available. Please install Python 3.6+ and try again." -ForegroundColor Red
    exit 1
}

# Check if required Python modules are installed
Write-Host "Checking required Python modules..." -ForegroundColor Cyan
$modulesInstalled = $true

function Check-Module {
    param (
        [string]$ModuleName
    )
    
    try {
        python -c "import $ModuleName"
        Write-Host "✓ $ModuleName is installed" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "✗ $ModuleName is not installed" -ForegroundColor Yellow
        return $false
    }
}

$requiredModules = @("requests", "json", "argparse", "logging", "datetime")
foreach ($module in $requiredModules) {
    if (-not (Check-Module -ModuleName $module)) {
        $modulesInstalled = $false
    }
}

if (-not $modulesInstalled) {
    Write-Host "Installing required modules..." -ForegroundColor Yellow
    pip install requests
}

# Run the verification script
Write-Host "`nRunning deployment verification script..." -ForegroundColor Cyan
python verify_deployment.py --verbose
$scriptExitCode = $LASTEXITCODE

if ($scriptExitCode -eq 0) {
    Write-Host "`n✅ Deployment verification completed successfully!" -ForegroundColor Green
    
    # Check if results file exists
    if (Test-Path -Path "DEPLOYMENT_TEST_RESULTS.md") {
        Write-Host "Results saved to DEPLOYMENT_TEST_RESULTS.md" -ForegroundColor Green
        
        # Display summary from results file
        Write-Host "`nSummary of deployment verification:" -ForegroundColor Cyan
        $content = Get-Content -Path "DEPLOYMENT_TEST_RESULTS.md" -Raw
        if ($content -match "## Summary\s+\*(.*?)\*\s+\*(.*?)\*\s+\*(.*?)\*\s+\*(.*?)\*") {
            Write-Host $matches[1] -ForegroundColor Cyan
            Write-Host $matches[2] -ForegroundColor Cyan
            Write-Host $matches[3] -ForegroundColor Cyan
            Write-Host $matches[4] -ForegroundColor Cyan
        }
        
        # Check if any issues were detected
        if ($content -match "## Issues Detected") {
            Write-Host "`nIssues were detected during verification:" -ForegroundColor Yellow
            if ($content -match "## Issues Detected\s+(.*?)##") {
                Write-Host $matches[1] -ForegroundColor Yellow
            }
        }
        else {
            Write-Host "`nNo issues detected during verification." -ForegroundColor Green
        }
    }
    else {
        Write-Host "Warning: Results file not found." -ForegroundColor Yellow
    }
    
    # Update the deployment status in DEPLOYMENT_COMPLETION_GUIDE.md
    Write-Host "`nUpdating deployment status in DEPLOYMENT_COMPLETION_GUIDE.md..." -ForegroundColor Cyan
    
    # Check if we have permission to update the file
    try {
        if (Test-Path -Path "DEPLOYMENT_COMPLETION_GUIDE.md") {
            $deploymentGuide = Get-Content -Path "DEPLOYMENT_COMPLETION_GUIDE.md" -Raw
            
            $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
            $updatedGuide = $deploymentGuide -replace "(?<=\*\*Date:.*?\*\*)", " (Last verified: $timestamp)"
            
            Set-Content -Path "DEPLOYMENT_COMPLETION_GUIDE.md" -Value $updatedGuide
            Write-Host "Deployment guide updated with verification timestamp." -ForegroundColor Green
            
            # Also add note to the test results
            Add-Content -Path "DEPLOYMENT_TEST_RESULTS.md" -Value "`n## Next Steps`n`nAll deployment verification tests have passed successfully. The system is fully operational and ready for use. The deployment guide has been updated with the latest verification timestamp.`n`nRefer to the [Comprehensive Deployment Checklist](./COMPREHENSIVE_DEPLOYMENT_CHECKLIST.md) for any manual verification steps that may be needed.`n"
        }
        else {
            Write-Host "Warning: DEPLOYMENT_COMPLETION_GUIDE.md not found." -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host "Warning: Could not update deployment guide file." -ForegroundColor Yellow
        Write-Host $_.Exception.Message -ForegroundColor Red
    }
    
    # Recommend next steps
    Write-Host "`nRecommended next steps:" -ForegroundColor Cyan
    Write-Host "1. Review the deployment verification results"
    Write-Host "2. Check for any issues and resolve them"
    Write-Host "3. Use the comprehensive deployment checklist for manual verification steps"
    Write-Host "4. Commit the updated verification files to your repository"
}
else {
    Write-Host "`n❌ Deployment verification failed!" -ForegroundColor Red
    Write-Host "Please review the log for details on the issues detected." -ForegroundColor Red
    
    # Check if results file exists
    if (Test-Path -Path "DEPLOYMENT_TEST_RESULTS.md") {
        Write-Host "Results and issues saved to DEPLOYMENT_TEST_RESULTS.md" -ForegroundColor Yellow
        
        # Add remediation steps to the test results
        Add-Content -Path "DEPLOYMENT_TEST_RESULTS.md" -Value "`n## Remediation Steps`n`nDeployment verification tests have failed. Please take the following steps to resolve the issues:`n`n1. Review the issues section above for specific problems detected`n2. Check the Railway logs for any backend errors`n3. Verify Supabase connection parameters in your .env.railway file`n4. Ensure all API endpoints are properly configured`n5. Run the verification script again after fixing issues`n"
    }
    
    # Recommend troubleshooting steps
    Write-Host "`nTroubleshooting steps:" -ForegroundColor Cyan
    Write-Host "1. Check if Railway backend is running properly (railway status)"
    Write-Host "2. Verify database connection strings in .env.railway"
    Write-Host "3. Check the API endpoints in config.js"
    Write-Host "4. Review logs for specific error messages"
    Write-Host "5. Run individual verification steps from the script"
}

Write-Host "`nDeployment verification process completed." -ForegroundColor Cyan
