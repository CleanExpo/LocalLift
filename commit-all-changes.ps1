# PowerShell script to commit all pending changes

# Initialize git repository if it doesn't exist
if (-not (Test-Path ".git")) {
    Write-Host "Initializing git repository..."
    git init
}

# Add all pending changes
Write-Host "Adding all pending changes to the staging area..."
git add .

# Commit the changes
git commit -m "Complete LocalLift Deployment MCP implementation

- Fixed Railway health check system with plain text response
- Enhanced Docker configuration with security and health checks
- Added specialized railway_entry.py for proper initialization
- Fixed Supabase client integration with proper error handling
- Standardized URLs across all deployment components
- Updated deployment documentation with Supabase setup details
- Added CORS configuration for proper frontend/backend communication
- Enhanced all deployment scripts for consistency"

Write-Host "All changes committed successfully!"
Write-Host "You can now push these changes to your remote repository with 'git push'"
