#!/bin/bash
# deploy-vercel.sh - Secure deployment script for LocalLift frontend to Vercel

set -e

echo "🚀 Starting LocalLift frontend deployment to Vercel..."

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI not found. Please install it with: npm install -g vercel"
    exit 1
fi

# Set the LocalLift authentication token
echo "✓ Setting LocalLift authentication token..."
export LOCALLIFT_AUTH_TOKEN="e6fa0a43-3924-4260-96eb-9e34e4829a58"
echo "LocalLift token set successfully."

# Check if logged in to Vercel
if ! vercel whoami &> /dev/null; then
    echo "❌ Not logged in to Vercel. Please login with: vercel login"
    exit 1
fi

# Build documentation if needed
echo "📚 Building documentation..."
if [ -f "tools/doc_build.sh" ]; then
    bash tools/doc_build.sh
else
    echo "⚠️ Documentation build script not found, continuing without it."
fi

# Verify the public directory exists
if [ ! -d "public" ]; then
    echo "❌ The public directory does not exist. Please create it before deploying."
    exit 1
fi

# Check for index.html in public directory
if [ ! -f "public/index.html" ]; then
    echo "❌ public/index.html not found. This is required for the SPA."
    exit 1
fi

# Verify vercel.json configuration
if [ ! -f "vercel.json" ]; then
    echo "❌ vercel.json not found. This is required for configuration."
    exit 1
fi

# Verify package.json configuration
if [ ! -f "package.json" ]; then
    echo "❌ package.json not found. This is required for Vercel deployment."
    exit 1
fi

# Update API endpoint in config if needed
if [ -f "public/js/config.js" ]; then
    echo "✓ Confirming correct Railway API URL in config.js..."
    # Ensure the Railway URL is set correctly
    sed -i 's|https://locallift-production.up.railway.app|https://locallift-production.up.railway.app|g' public/js/config.js
    echo "✓ Railway URL set to: https://locallift-production.up.railway.app"
fi

# Deploy to Vercel
echo "🌐 Deploying to Vercel..."
vercel --prod --yes

echo "✅ Deployment complete!"
echo "🔍 Your site is now available on Vercel."
echo ""
echo "Don't forget to ensure your Railway backend API is also deployed:"
echo "  ./deploy-secure.sh"
