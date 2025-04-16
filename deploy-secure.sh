#!/bin/bash
# deploy-secure.sh - Secure deployment script for LocalLift to Railway

set -e

echo "🚀 Starting LocalLift secure deployment to Railway..."

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Please install it with: npm install -g @railway/cli"
    exit 1
fi

# Check if logged in to Railway
railway whoami &> /dev/null || {
    echo "❌ Not logged in to Railway. Please login with: railway login"
    exit 1
}

# Link to the correct project if not already linked
railway link -p 0e58b112-f5f5-4285-ad1f-f47d1481045b

# Set the LocalLift authentication token
echo "✓ Setting LocalLift authentication token..."
export LOCALLIFT_AUTH_TOKEN="e6fa0a43-3924-4260-96eb-9e34e4829a58"

# Ensure environment variables are properly set
echo "✓ Verifying environment variables..."
if [ ! -f .env.railway ]; then
    echo "⚠️ Warning: .env.railway file not found. Creating from template..."
    cp .env.template .env.railway
    echo "⚠️ Please update .env.railway with actual values before proceeding."
    exit 1
fi

# Verify railway.json exists
if [ ! -f "railway.json" ]; then
    echo "❌ railway.json not found. This is required for deployment configuration."
    exit 1
fi

# Deploy to Railway
echo "🚂 Deploying to Railway with advanced configuration..."
railway up

echo "✅ Deployment complete!"
echo "🔍 You can check the status at: https://railway.app/project/0e58b112-f5f5-4285-ad1f-f47d1481045b"
echo "🌐 Multi-region deployment configured (asia-southeast1-eqsg3a)"
echo "🌐 Your app will be available at: https://locallift-production.up.railway.app"

# Run health check
echo "🩺 Running health check..."
sleep 10
if curl -s https://locallift-production.up.railway.app/api/health | grep -q "ok"; then
    echo "✅ Health check passed!"
else
    echo "⚠️ Health check failed. Please check Railway logs for details."
fi
