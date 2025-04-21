# MCP-Powered Deployment Automation

A comprehensive suite of tools for automating deployment troubleshooting, configuration, and verification using Model Context Protocol (MCP) technology.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.6%2B-blue)](https://www.python.org/downloads/)
[![PowerShell Version](https://img.shields.io/badge/powershell-5.1%2B-blue)](https://docs.microsoft.com/en-us/powershell/)

## 📋 Overview

This repository contains a suite of tools for automated discovery, testing, configuration, and fixing of deployment issues using Model Context Protocol (MCP) technology. The tools are designed to work with Railway, Vercel, and other cloud hosting providers.

### Key Features

- **Endpoint Discovery**: Automatically discover working endpoints when primary ones are down
- **Automated Fixing**: Fix common deployment issues in code and configuration
- **Comprehensive Verification**: Test all components to ensure they're working correctly
- **API Integration**: Deploy directly to Railway and Vercel with API tokens
- **Detailed Reporting**: Generate logs and reports for troubleshooting

## 🚀 Getting Started

### Prerequisites

- Python 3.6 or higher
- PowerShell 5.1 or higher (for Windows users)
- Node.js and npm
- Git

### Quick Installation

#### Option 1: One-Click Deployment and Run

For the fastest setup, run the automated deployment script:

```bash
# Run the deploy and run script
.\deploy_and_run.ps1
```

This script will:
1. Initialize a local Git repository
2. Install all required dependencies
3. Set up the necessary directories
4. Run the automation in non-interactive mode

#### Option 2: Manual Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
npm install -g hyperbrowser-mcp @modelcontextprotocol/fetch-mcp
```

2. Create necessary directories:
```bash
mkdir -p mcp-env deployment-logs
```

### Running the Automation

Run the main automation script:

```powershell
# On Windows with PowerShell
.\run_auto_deployment.ps1

# On Linux/macOS or with Python directly
python src/auto_deployment_fixer.py
```

## 🔍 Components

### 1. run_auto_deployment.ps1

The main PowerShell script that coordinates the entire automation process:

- Checks environment and installs missing dependencies
- Manages the execution of all other tools
- Provides interactive prompts for API tokens
- Generates comprehensive deployment status reports

### 2. auto_deployment_fixer.py

A comprehensive Python tool that:

- Corrects PORT configuration in FastAPI/Flask applications
- Updates API endpoints in frontend configurations
- Deploys to Railway and configures Vercel (with API tokens)
- Verifies that all components are working correctly

### 3. mcp_endpoint_discovery.py

A Python script that uses MCP servers to:

- Perform comprehensive endpoint discovery and testing
- Identify working alternatives when primary endpoints are down
- Generate corrected configuration files with working endpoints

### 4. Platform Modules

Located in `src/platforms/`, these modules provide:

- Railway integration for deployment and configuration
- Vercel integration for frontend deployments
- Extensible interface for adding new platforms

## 💻 Usage Examples

### Basic Usage

```powershell
# Navigate to your project directory
cd /path/to/your/project

# Copy the deployment automation files
git clone <your-repo-url> automation
cd automation

# Run the automated deployment process
.\run_auto_deployment.ps1
```

### With API Tokens

```powershell
# Run with API tokens for full automation
.\run_auto_deployment.ps1
# When prompted, provide your Railway and Vercel API tokens
```

### Python-only Usage

```bash
# For users without PowerShell
python src/auto_deployment_fixer.py --railway-token YOUR_RAILWAY_TOKEN --vercel-token YOUR_VERCEL_TOKEN
```

### Fixing Specific Issues

```powershell
# Fix only PORT configuration issues
python src/auto_deployment_fixer.py --fix-port-only

# Update only config.js with correct API endpoints
python src/auto_deployment_fixer.py --update-config-only

# Verify deployment without making changes
python src/auto_deployment_fixer.py --verify-only
```

## 🛠️ Customization

### Configuration Files

- `config.json`: Configure default endpoints and alternatives
- `.env.example`: Example environment variables file

### Adding New Platforms

The system is designed to be extensible. To add support for a new platform:

1. Create a new module in the `src/platforms` directory
2. Implement the required interface methods
3. Register the platform in `src/platforms/__init__.py`

## 📚 Documentation

For more detailed information, see:

- [AUTOMATED_SETUP.md](./AUTOMATED_SETUP.md) - Instructions for setting up automated runs
- [CONTRIBUTING.md](./CONTRIBUTING.md) - Guidelines for contributors
- [EXAMPLE_USAGE.md](./EXAMPLE_USAGE.md) - More detailed usage examples
- [CHANGELOG.md](./CHANGELOG.md) - Version history and changes

## ⭐ Publish This Project!

To share this project, publish it on GitHub:

1. Create a new repository on GitHub
2. Push this local repository to GitHub:
```bash
# Initialize the local repository
git init
git add .
git commit -m "Initial commit"

# Add your remote repository
git remote add origin https://github.com/yourusername/deployment-automation.git
git push -u origin main
```

3. Update all references to the repository URL in documentation

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Model Context Protocol](https://github.com/modelcontextprotocol) - For providing the MCP technology
- [Hyperbrowser MCP](https://github.com/hyperbrowserai/mcp) - For providing browser automation capabilities
- [Fetch MCP](https://github.com/modelcontextprotocol/fetch-mcp) - For providing HTTP request capabilities
