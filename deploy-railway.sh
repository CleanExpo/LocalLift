#!/bin/bash
# Railway Deployment Script for LocalLift
# This script handles the deployment process for Railway

echo "LocalLift Railway Deployment"
echo "==========================="

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null
then
    echo "Railway CLI not found. Installing..."
    npm i -g @railway/cli
fi

# Check if user is logged in to Railway
if ! railway whoami &> /dev/null
then
    echo "Please log in to Railway:"
    railway login
fi

# Commit latest changes
echo "Committing latest changes..."
git add .env.railway railway.json Dockerfile main.py
git commit -m "🚀 Update Railway deployment configuration"

# Push to Railway
echo "Deploying to Railway..."
railway up

echo "Deployment initiated!"
echo "Note: It may take a few minutes for changes to propagate."
echo "You can check the deployment status in the Railway dashboard."
echo "Once deployed, your API will be available at:"
echo "https://local-lift-production.up.railway.app"
echo "Health check endpoint: https://local-lift-production.up.railway.app/health"
