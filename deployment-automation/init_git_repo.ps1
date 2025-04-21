# Initialize Git repository for MCP-Powered Deployment Automation
# This script prepares the repository for GitHub

# Set error action preference to stop on errors
$ErrorActionPreference = "Stop"

Write-Host "=== Initializing Git Repository for MCP-Powered Deployment Automation ===" -ForegroundColor Cyan

# Check if Git is installed
if (-not (Get-Command "git" -ErrorAction SilentlyContinue)) {
    Write-Host "Git is not installed or not in PATH. Please install Git and try again." -ForegroundColor Red
    exit 1
}

# Check if we're in the right directory
$ExpectedFiles = @("README.md", "LICENSE", "requirements.txt", ".gitignore", "run_auto_deployment.ps1")
$MissingFiles = $ExpectedFiles | Where-Object { -not (Test-Path $_) }

if ($MissingFiles.Count -gt 0) {
    Write-Host "Missing expected files: $($MissingFiles -join ', ')" -ForegroundColor Yellow
    Write-Host "Make sure you run this script from the deployment-automation directory." -ForegroundColor Yellow
    $Continue = Read-Host "Continue anyway? (y/n)"
    if ($Continue -ne 'y') {
        exit 1
    }
}

# Initialize Git repository
Write-Host "Initializing Git repository..." -ForegroundColor Green
git init

# Create src directory if it doesn't exist
if (-not (Test-Path "src")) {
    Write-Host "Creating src directory..." -ForegroundColor Green
    New-Item -ItemType Directory -Path "src" | Out-Null
}

# Create platforms directory if it doesn't exist
if (-not (Test-Path "src\platforms")) {
    Write-Host "Creating platforms directory..." -ForegroundColor Green
    New-Item -ItemType Directory -Path "src\platforms" | Out-Null
}

# Create example config.json
$ConfigJson = @{
    "platforms" = @{
        "railway" = @{
            "default_endpoint" = "https://locallift-api.up.railway.app"
            "alternatives" = @(
                "https://locallift-backend.up.railway.app",
                "https://locallift-production.up.railway.app"
            )
        }
        "vercel" = @{
            "default_endpoint" = "https://locallift.vercel.app"
            "alternatives" = @(
                "https://local-lift.vercel.app",
                "https://local-lift-admin.vercel.app"
            )
        }
    }
    "settings" = @{
        "timeout_seconds" = 10
        "max_attempts" = 3
        "logging_level" = "INFO"
    }
}
Write-Host "Creating config.json..." -ForegroundColor Green
$ConfigJson | ConvertTo-Json -Depth 4 | Set-Content "config.json"

# Create .env.example
$EnvExample = @"
# Backend (Railway) Configuration
BACKEND_URL=https://your-railway-app.up.railway.app
API_URL=https://your-railway-app.up.railway.app/api
HEALTH_ENDPOINT=https://your-railway-app.up.railway.app/health

# Frontend (Vercel) Configuration
FRONTEND_URL=https://your-app.vercel.app
LOGIN_URL=https://your-app.vercel.app/login
DASHBOARD_URL=https://your-app.vercel.app/dashboard

# API Tokens (DO NOT COMMIT THESE!)
RAILWAY_TOKEN=your_railway_token
VERCEL_TOKEN=your_vercel_token

# Authentication Settings
REQUIRES_AUTH=true
"@
Write-Host "Creating .env.example..." -ForegroundColor Green
$EnvExample | Set-Content ".env.example"

# Create platforms/__init__.py
$PlatformsInit = @"
"""
Platform modules for deployment automation
"""

from .railway import RailwayPlatform
from .vercel import VercelPlatform

__all__ = ['RailwayPlatform', 'VercelPlatform']
"@
Write-Host "Creating platforms/__init__.py..." -ForegroundColor Green
New-Item -ItemType Directory -Path "src\platforms" -Force | Out-Null
$PlatformsInit | Set-Content "src\platforms\__init__.py"

# Create empty railway.py and vercel.py in platforms directory
Write-Host "Creating platform module files..." -ForegroundColor Green
@"
"""
Railway platform integration
"""

class RailwayPlatform:
    """Railway platform handler"""
    
    def __init__(self, token=None):
        self.token = token
        
    def deploy(self):
        """Deploy to Railway"""
        pass
        
    def get_logs(self):
        """Get logs from Railway"""
        pass
"@ | Set-Content "src\platforms\railway.py"

@"
"""
Vercel platform integration
"""

class VercelPlatform:
    """Vercel platform handler"""
    
    def __init__(self, token=None):
        self.token = token
        
    def deploy(self):
        """Deploy to Vercel"""
        pass
        
    def get_logs(self):
        """Get logs from Vercel"""
        pass
"@ | Set-Content "src\platforms\vercel.py"

# Create setup.py
$SetupPy = @"
from setuptools import setup, find_packages

setup(
    name="mcp-deployment-automation",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.1",
        "python-dotenv>=0.19.0",
        "colorama>=0.4.4",
    ],
    entry_points={
        "console_scripts": [
            "mcp-discover=src.mcp_endpoint_discovery:main",
            "mcp-fix=src.auto_deployment_fixer:main",
        ],
    },
    python_requires=">=3.6",
    author="LocalLift",
    author_email="info@locallift.com",
    description="MCP-powered deployment automation tools",
    keywords="deployment, automation, mcp",
    url="https://github.com/locallift/deployment-automation",
    project_urls={
        "Bug Tracker": "https://github.com/locallift/deployment-automation/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
"@
Write-Host "Creating setup.py..." -ForegroundColor Green
$SetupPy | Set-Content "setup.py"

# Add all files to Git
Write-Host "Adding files to Git..." -ForegroundColor Green
git add .

# Make initial commit
Write-Host "Making initial commit..." -ForegroundColor Green
git commit -m "Initial commit for MCP-Powered Deployment Automation"

# Instructions for pushing to GitHub
Write-Host @"

=== Repository initialized successfully! ===

To push this to GitHub:
1. Create a new repository on GitHub (https://github.com/new)
2. Link your local repository with the remote:
   git remote add origin https://github.com/yourusername/deployment-automation.git
3. Push your changes:
   git push -u origin main

=== Additional steps to complete the setup ===

1. Add your implementation files to the src directory:
   - Copy mcp_endpoint_discovery.py to src/
   - Copy auto_deployment_fixer.py to src/

2. Ensure any hardcoded paths are made relative

3. Update documentation if needed
"@ -ForegroundColor Cyan
