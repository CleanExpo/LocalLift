#!/bin/bash
# commit-deploy-changes.sh - Commit and push deployment configuration changes

set -e

echo "🔍 Checking Git status..."
git status

echo ""
echo "🚀 Adding deployment configuration files..."

# Add all the new deployment files
git add railway.toml
git add package.json
git add vercel.json
git add deploy-secure.sh
git add deploy-vercel.sh
git add deploy-vercel.ps1
git add prepare-vercel-deploy.sh
git add prepare-vercel-deploy.ps1
git add DEPLOYMENT.md
git add RAILWAY_DEPLOYMENT.md

# Make the script executable
chmod +x deploy-secure.sh
chmod +x deploy-vercel.sh
chmod +x prepare-vercel-deploy.sh

echo ""
echo "✓ Files staged for commit. Current changes:"
git status

echo ""
echo "📝 Committing changes..."
git commit -m "Add comprehensive deployment configuration for Railway and Vercel"

echo ""
echo "⬆️ Pushing changes to remote repository..."
git push

echo ""
echo "✅ Changes committed and pushed successfully!"
echo "The LocalLift deployment configuration is now ready for use."
