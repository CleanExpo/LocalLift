#!/bin/bash
# Script to commit all deployment documentation and configuration files to git

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "Initializing git repository..."
    git init
fi

# Add all deployment documentation files
echo "Adding documentation files..."
git add README.md
git add DEPLOYMENT_GUIDE.md
git add GITHUB_ACTIONS_GUIDE.md
git add RAILWAY_DEPLOYMENT.md

# Add configuration files
echo "Adding configuration files..."
git add railway.json
git add railway.toml
git add Dockerfile
git add railway_entry.py
git add .env.railway
git add vercel.json
git add public/js/config.js
git add public/config.js

# Add deployment tools
echo "Adding deployment tools..."
git add tools/pre_deploy_check.py
git add tools/check_null_bytes.py
git add tools/fix_null_bytes.py
git add tools/cleanup_temp_files.py
git add tools/monitor_deployment.py

# Add deployment scripts
echo "Adding deployment scripts..."
git add deploy-railway.ps1
git add deploy-vercel.ps1
git add .github/workflows/deploy.yml
git add commit-documentation.sh

# Commit changes
echo "Committing changes..."
git commit -m "Add LocalLift deployment system with documentation and tools

This commit includes:
- Comprehensive deployment documentation
- Railway backend configuration
- Vercel frontend configuration
- Deployment validation and monitoring tools
- GitHub Actions CI/CD workflow
- Null byte detection and fixing tools"

echo "Deployment documentation committed successfully!"
echo "Push to remote repository with: git push origin main"
