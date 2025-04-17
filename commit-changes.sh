#!/bin/bash
# Shell script to commit deployment changes

# Initialize git repository if it doesn't exist
if [ ! -d ".git" ]; then
    echo "Initializing git repository..."
    git init
fi

# Add all the modified files
git add Dockerfile
git add railway_entry.py
git add core/supabase/client.py
git add deploy-vercel.sh
git add deploy-vercel.ps1
git add railway.json
git add .env.railway
git add DEPLOYMENT.md
git add SUPABASE_SETUP.md
git add public/js/config.js
git add railway.toml
git add main.py

# Commit the changes
git commit -m "Comprehensive deployment enhancements

- Fixed Railway health check system with plain text response
- Enhanced Docker configuration with security and health checks
- Added specialized railway_entry.py for proper initialization
- Fixed Supabase client integration with proper error handling
- Standardized URLs across all deployment components
- Updated deployment documentation with Supabase setup details
- Added CORS configuration for proper frontend/backend communication
- Enhanced all deployment scripts for consistency"

echo "Changes committed successfully!"
