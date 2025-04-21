# MCP Endpoint Discovery Tools

This document provides detailed documentation for the MCP-based endpoint discovery and correction tools created for the LocalLift deployment.

## Overview

These tools leverage Model Context Protocol (MCP) servers to systematically discover, test, and configure working endpoints for the LocalLift application. They address deployment issues by automatically finding alternative endpoints when primary ones are not working.

## Tool Descriptions

### 1. Python Implementation: `mcp_endpoint_discovery.py`

This is the primary tool, providing a comprehensive endpoint discovery and testing solution using Python. It interfaces with MCP servers to test endpoints, discover alternatives, and generate corrected configuration files.

#### Key Features:

- Automatically tests all known endpoints and common variations
- Finds alternative endpoints based on naming patterns
- Creates environment configuration with working endpoints
- Updates frontend configuration files to use working endpoints
- Generates detailed reports on endpoint status

#### Prerequisites:

- Python 3.6+
- Required Python packages:
  - `requests`
- MCP servers:
  - `hyperbrowser-mcp`
  - `fetch-mcp`

#### Technical Implementation:

The tool performs the following operations:
1. Starts MCP servers for testing
2. Tests various Railway (backend) endpoints
3. Tests Vercel (frontend) endpoints
4. Identifies working alternatives
5. Generates configuration files with correct endpoints
6. Creates a summary report with findings and recommendations

### 2. PowerShell Implementation: `endpoint-diagnosis-mcp.ps1`

This is an alternative implementation using PowerShell, which provides similar functionality as the Python version but with native Windows scripting.

#### Key Features:

- Checks and installs required MCP servers
- Creates configuration directory structure
- Tests multiple endpoint variations
- Generates environment files with working endpoints
- Updates frontend configuration with correct API URL

#### Prerequisites:

- PowerShell 5.1+
- Node.js (for running MCP servers)
- MCP servers:
  - `hyperbrowser-mcp`
  - `fetch-mcp`

## Installation Guide

### Installing Required Dependencies

1. **Python Packages**:
   ```
   pip install requests
   ```

2. **MCP Servers**:
   ```
   npm install -g hyperbrowser-mcp
   npm install -g @modelcontextprotocol/fetch-mcp
   ```

## Usage Guide

### Running the Python Tool

```bash
# Navigate to the project directory
cd C:\Users\PhillMcGurk\Desktop\LocalLift

# Run the tool
python mcp_endpoint_discovery.py
```

### Running the PowerShell Tool

```powershell
# Navigate to the project directory
cd C:\Users\PhillMcGurk\Desktop\LocalLift

# Run the tool
.\endpoint-diagnosis-mcp.ps1
```

## Output Files

The tools generate several files in the `mcp-env` directory:

1. **endpoints.json**: Comprehensive endpoint configuration
2. **railway_test_results.json**: Results of Railway endpoint tests
3. **vercel_test_results.json**: Results of Vercel endpoint tests
4. **.env**: Environment configuration with working endpoints
5. **endpoint_discovery_summary.txt**: Summary of findings and recommendations

## Applying the Results

After running the tools, you should:

1. Review the generated files in the `mcp-env` directory
2. Check which endpoints were found to be working
3. Update your deployment configurations to use these endpoints:
   - Railway environment variables
   - Vercel environment variables
   - Frontend configuration files

## Troubleshooting

### Common Issues and Solutions

1. **MCP servers fail to start**:
   - Check that Node.js is properly installed
   - Verify that the MCP packages are globally installed
   - Try reinstalling the MCP packages

2. **Cannot find any working endpoints**:
   - Check the Railway dashboard to verify app deployment
   - Verify that your application is properly configured to use the PORT environment variable
   - Check the Railway logs for startup errors

3. **Configuration file updates fail**:
   - Check file permissions
   - Run the script with administrator privileges

## Technical Details

### Endpoint Discovery Methodology

The tools use a systematic approach to discover working endpoints:

1. **Known endpoint testing**: Tests endpoints specified in the configuration
2. **Pattern-based discovery**: Generates variations of known endpoints
3. **Domain-specific patterns**: Tests common Railway and Vercel URL patterns
4. **Path variations**: Tests different path combinations (/api, /health, etc.)

### MCP Integration

The tools use two MCP servers:

1. **fetch-mcp**: For simple HTTP requests to test endpoint availability
2. **hyperbrowser-mcp**: For browser-based testing to handle authentication and redirects

## Extending the Tools

You can extend these tools by:

1. Adding more endpoint patterns to test
2. Implementing additional tests for specific endpoints
3. Creating custom configuration generators for other deployment platforms

## Conclusion

These MCP-based endpoint discovery tools provide a powerful and automated approach to diagnosing and fixing deployment endpoint issues. By leveraging these tools, you can quickly identify working endpoints and configure your application accordingly, even when the primary endpoints are not functioning.
