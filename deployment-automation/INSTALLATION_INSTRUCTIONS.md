========= AUTOMATION DEPLOYMENT INSTRUCTIONS ==========

## Quick Installation

```bash
git clone https://github.com/locallift/deployment-automation.git
cd deployment-automation
./deploy_and_run.ps1
```

## Manual Installation

1. Clone the repository:
```bash
git clone https://github.com/locallift/deployment-automation.git
cd deployment-automation
```

2. Install dependencies:
```bash
pip install -r requirements.txt
npm install -g hyperbrowser-mcp @modelcontextprotocol/fetch-mcp
```

3. Run the automation manually:
```powershell
# On Windows
.\run_auto_deployment.ps1

# On Linux/macOS (requires PowerShell Core)
./run_auto_deployment.ps1
```

## Repository URL

GitHub Repository: [https://github.com/locallift/deployment-automation](https://github.com/locallift/deployment-automation)
