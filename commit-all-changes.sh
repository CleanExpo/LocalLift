#!/bin/bash
# Shell script to commit all pending changes

# Initialize git repository if it doesn't exist
if [ ! -d ".git" ]; then
    echo "Initializing git repository..."
    git init
fi

# Add all pending changes
echo "Adding all pending changes to the staging area..."
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

echo "All changes committed successfully!"
echo "You can now push these changes to your remote repository with 'git push'"
