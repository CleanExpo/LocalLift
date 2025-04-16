#!/bin/bash
# prepare-vercel-deploy.sh - Prepare assets for Vercel deployment

set -e

echo "🔧 Preparing assets for Vercel deployment..."

# Create the public/js directory if it doesn't exist
mkdir -p public/js

# Copy configuration file to public directory
echo "📝 Copying configuration files to public directory..."
cp static/js/config.js public/js/config.js

# Ensure index.html references the correct config.js location
if [ -f "public/index.html" ]; then
    echo "✓ Checking index.html for config.js reference..."
    
    # Check if index.html includes config.js
    if grep -q "config.js" public/index.html; then
        # If it references the static path, update it to the public path
        sed -i 's|src="static/js/config.js"|src="js/config.js"|g' public/index.html
        sed -i 's|src="/static/js/config.js"|src="/js/config.js"|g' public/index.html
    else
        echo "⚠️ config.js is not referenced in index.html. You may need to add it manually."
    fi
else
    echo "❌ public/index.html not found. Please ensure it exists before deployment."
    exit 1
fi

# Copy any other necessary static assets
echo "📦 Copying additional static assets..."

# Copy CSS files
cp -r static/css public/ 2>/dev/null || echo "No static/css directory found."

# Copy image files if they exist
if [ -d "static/images" ]; then
    cp -r static/images public/
fi

# Copy any additional JS files
cp static/js/*.js public/js/ 2>/dev/null || echo "No additional JS files found."

echo "✅ Preparation complete! The site is ready for Vercel deployment."
echo "To deploy, run: ./deploy-vercel.sh"
