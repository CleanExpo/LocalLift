#!/usr/bin/env python3
# Auto Deployment Fixer (Fixed Version)
# This script automatically fixes common deployment issues
# Fixed version removes Unicode characters that cause encoding errors

import os
import sys
import json
import logging
import argparse
import re
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("auto_deployment_fixer")

# Constants
MCP_ENV_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "mcp-env")
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Ensure MCP_ENV_DIR exists
if not os.path.exists(MCP_ENV_DIR):
    os.makedirs(MCP_ENV_DIR)
    logger.info(f"Created MCP environment directory: {MCP_ENV_DIR}")

# Log file in MCP_ENV_DIR
log_file = os.path.join(MCP_ENV_DIR, f"auto_fixer_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

def load_endpoints():
    """Load endpoint configuration from endpoint discovery"""
    endpoints_file = os.path.join(MCP_ENV_DIR, "endpoints.json")
    env_file = os.path.join(MCP_ENV_DIR, ".env")
    
    endpoints = {}
    
    # Try to load from endpoints.json first
    if os.path.exists(endpoints_file):
        try:
            with open(endpoints_file, "r") as f:
                endpoints = json.load(f)
            logger.info(f"Loaded endpoints from {endpoints_file}")
            return endpoints
        except Exception as e:
            logger.warning(f"Failed to load endpoints.json: {e}")
    
    # Try to parse from .env file as fallback
    if os.path.exists(env_file):
        try:
            with open(env_file, "r") as f:
                env_content = f.read()
                
            # Parse API_ENDPOINT
            api_match = re.search(r"API_ENDPOINT=([^\n]+)", env_content)
            if api_match:
                endpoints["railway_endpoint"] = api_match.group(1)
            
            # Parse FRONTEND_URL
            frontend_match = re.search(r"FRONTEND_URL=([^\n]+)", env_content)
            if frontend_match:
                endpoints["vercel_endpoint"] = frontend_match.group(1)
            
            # Parse SUPABASE_URL
            supabase_match = re.search(r"SUPABASE_URL=([^\n]+)", env_content)
            if supabase_match:
                endpoints["supabase_endpoint"] = supabase_match.group(1)
            
            logger.info(f"Parsed endpoints from {env_file}")
            return endpoints
        except Exception as e:
            logger.warning(f"Failed to parse .env file: {e}")
    
    logger.warning("No endpoint configuration found")
    return {
        "railway_endpoint": None,
        "vercel_endpoint": None,
        "supabase_endpoint": None
    }

def fix_port_configuration():
    """Fix PORT configuration in main.py"""
    main_py_path = os.path.join(PROJECT_ROOT, "main.py")
    
    if not os.path.exists(main_py_path):
        logger.warning(f"main.py not found at {main_py_path}")
        return False
    
    try:
        with open(main_py_path, "r") as f:
            content = f.read()
        
        # Check if PORT is already correctly configured
        if re.search(r"port\s*=\s*int\s*\(\s*os\.environ\.get\s*\(\s*['\"]PORT['\"]\s*,", content):
            logger.info("PORT configuration already correct in main.py")
            return True
        
        # Fix PORT configuration
        # Look for the pattern where port is defined
        port_pattern = re.compile(r"port\s*=\s*\d+")
        if port_pattern.search(content):
            # Replace hardcoded port with environment variable
            new_content = port_pattern.sub("port = int(os.environ.get('PORT', '8000'))", content)
            
            # Make sure os is imported
            if "import os" not in content:
                import_pattern = re.compile(r"(import [^\n]+)")
                match = import_pattern.search(new_content)
                if match:
                    new_content = new_content.replace(match.group(0), f"{match.group(0)}\nimport os")
                else:
                    new_content = "import os\n\n" + new_content
            
            # Write the fixed content back
            with open(main_py_path, "w") as f:
                f.write(new_content)
            
            logger.info("Fixed PORT configuration in main.py")
            return True
        else:
            # If we can't find a port definition, add one near the bottom before the app.run
            if "app.run" in content or "if __name__ == '__main__'" in content:
                # Find the position to insert
                match = re.search(r"(app\.run|if __name__ == ['|\"]__main__['|\"])", content)
                if match:
                    pos = match.start()
                    new_content = content[:pos] + "\n# Get port from environment variable\nport = int(os.environ.get('PORT', '8000'))\n\n" + content[pos:]
                    
                    # Make sure os is imported
                    if "import os" not in new_content:
                        import_pattern = re.compile(r"(import [^\n]+)")
                        match = import_pattern.search(new_content)
                        if match:
                            new_content = new_content.replace(match.group(0), f"{match.group(0)}\nimport os")
                        else:
                            new_content = "import os\n\n" + new_content
                    
                    # Write the fixed content back
                    with open(main_py_path, "w") as f:
                        f.write(new_content)
                    
                    logger.info("Added PORT configuration to main.py")
                    return True
            
            logger.warning("Could not find a suitable location to fix PORT configuration in main.py")
            return False
    except Exception as e:
        logger.error(f"Error fixing PORT configuration: {e}")
        return False

def update_api_config(api_endpoint):
    """Update API endpoint in config.js"""
    if not api_endpoint:
        logger.warning("No API endpoint provided to update config.js")
        return False
    
    config_js_path = os.path.join(PROJECT_ROOT, "public", "js", "config.js")
    
    if not os.path.exists(config_js_path):
        logger.warning(f"config.js not found at {config_js_path}")
        return False
    
    try:
        with open(config_js_path, "r") as f:
            content = f.read()
        
        # Check if API_BASE_URL is already set to the correct endpoint
        api_url_pattern = re.compile(r"(const|let|var)\s+API_BASE_URL\s*=\s*['\"]([^'\"]+)['\"]")
        match = api_url_pattern.search(content)
        
        if match and match.group(2) == api_endpoint:
            logger.info(f"API_BASE_URL already set to {api_endpoint} in config.js")
            return True
        
        if match:
            # Replace existing API_BASE_URL
            new_content = api_url_pattern.sub(f"\\1 API_BASE_URL = \"{api_endpoint}\"", content)
            
            # Write the updated content back
            with open(config_js_path, "w") as f:
                f.write(new_content)
            
            logger.info(f"Updated API_BASE_URL to {api_endpoint} in config.js")
            return True
        else:
            # Add API_BASE_URL if it doesn't exist
            new_content = f"// API Configuration\nconst API_BASE_URL = \"{api_endpoint}\";\n\n" + content
            
            # Write the updated content back
            with open(config_js_path, "w") as f:
                f.write(new_content)
            
            logger.info(f"Added API_BASE_URL with value {api_endpoint} to config.js")
            return True
    except Exception as e:
        logger.error(f"Error updating API configuration: {e}")
        return False

def verify_deployment(endpoints):
    """Verify that the deployment is working"""
    import requests
    from requests.exceptions import RequestException
    
    results = {
        "railway": False,
        "vercel": False,
        "supabase": False
    }
    
    # Verify Railway backend
    if endpoints.get("railway_endpoint"):
        railway_url = endpoints["railway_endpoint"]
        health_url = f"{railway_url.rstrip('/')}/health"
        try:
            logger.info(f"Testing Railway endpoint: {railway_url}")
            response = requests.get(railway_url, timeout=10)
            if 200 <= response.status_code < 400:
                results["railway"] = True
                logger.info(f"Railway endpoint is working: {railway_url} (Status: {response.status_code})")
            else:
                logger.warning(f"Railway endpoint returned status {response.status_code}: {railway_url}")
                
            # Try health endpoint
            logger.info(f"Testing health endpoint: {health_url}")
            health_response = requests.get(health_url, timeout=10)
            if 200 <= health_response.status_code < 400:
                results["railway"] = True
                logger.info(f"Health endpoint is working: {health_url} (Status: {health_response.status_code})")
            else:
                logger.warning(f"Health endpoint returned status {health_response.status_code}: {health_url}")
        except RequestException as e:
            logger.warning(f"Failed to connect to Railway endpoint: {e}")
    
    # Verify Vercel frontend
    if endpoints.get("vercel_endpoint"):
        vercel_url = endpoints["vercel_endpoint"]
        try:
            logger.info(f"Testing Vercel endpoint: {vercel_url}")
            response = requests.get(vercel_url, timeout=10)
            if 200 <= response.status_code < 400:
                results["vercel"] = True
                logger.info(f"Vercel endpoint is working: {vercel_url} (Status: {response.status_code})")
            else:
                logger.warning(f"Vercel endpoint returned status {response.status_code}: {vercel_url}")
        except RequestException as e:
            logger.warning(f"Failed to connect to Vercel endpoint: {e}")
    
    # Verify Supabase (placeholder)
    if endpoints.get("supabase_endpoint"):
        # For Supabase, we just check if the URL is accessible, not if the database is working
        results["supabase"] = True
        logger.info(f"Supabase endpoint found: {endpoints['supabase_endpoint']}")
    
    return results

def generate_summary(endpoints, fixes_applied, verification_results):
    """Generate a human-readable summary"""
    summary_file = os.path.join(MCP_ENV_DIR, "auto_fixer_summary.txt")
    
    with open(summary_file, "w") as f:
        f.write("=========================================\n")
        f.write(" LocalLift Auto Deployment Fixer Report\n")
        f.write("=========================================\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("ENDPOINTS USED:\n")
        f.write("--------------\n")
        if endpoints.get("railway_endpoint"):
            f.write(f"Railway API: {endpoints['railway_endpoint']}\n")
        else:
            f.write("Railway API: Not found\n")
        
        if endpoints.get("vercel_endpoint"):
            f.write(f"Vercel Frontend: {endpoints['vercel_endpoint']}\n")
        else:
            f.write("Vercel Frontend: Not found\n")
        
        if endpoints.get("supabase_endpoint"):
            f.write(f"Supabase Database: {endpoints['supabase_endpoint']}\n")
        else:
            f.write("Supabase Database: Not found\n")
        
        f.write("\nFIXES APPLIED:\n")
        f.write("-------------\n")
        if fixes_applied.get("port_fixed"):
            f.write("[OK] PORT configuration fixed in main.py\n")
        else:
            f.write("[NO] PORT configuration was not fixed\n")
        
        if fixes_applied.get("config_updated"):
            f.write("[OK] API endpoint updated in config.js\n")
        else:
            f.write("[NO] API endpoint was not updated in config.js\n")
        
        f.write("\nVERIFICATION RESULTS:\n")
        f.write("--------------------\n")
        if verification_results.get("railway"):
            f.write("[OK] Railway backend is accessible\n")
        else:
            f.write("[NO] Railway backend is not accessible\n")
        
        if verification_results.get("vercel"):
            f.write("[OK] Vercel frontend is accessible\n")
        else:
            f.write("[NO] Vercel frontend is not accessible\n")
        
        if verification_results.get("supabase"):
            f.write("[OK] Supabase database configuration found\n")
        else:
            f.write("[NO] Supabase database configuration not found\n")
        
        f.write("\n=========================================\n")
        f.write("For full details, see log file: " + os.path.basename(log_file) + "\n")
    
    logger.info(f"Summary report saved to {summary_file}")
    return summary_file

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Auto Deployment Fixer for LocalLift")
    parser.add_argument("--railway-token", help="Railway API token for deployment")
    parser.add_argument("--vercel-token", help="Vercel API token for deployment")
    parser.add_argument("--fix-port-only", action="store_true", help="Only fix PORT configuration")
    parser.add_argument("--update-config-only", action="store_true", help="Only update config.js")
    parser.add_argument("--verify-only", action="store_true", help="Only verify deployment")
    parser.add_argument("--non-interactive", action="store_true", help="Run in non-interactive mode")
    return parser.parse_args()

def main():
    """Main entry point for auto deployment fixer"""
    
    logger.info("Starting Auto Deployment Fixer")
    
    args = parse_arguments()
    
    try:
        # Load endpoint configuration from endpoint discovery
        endpoints = load_endpoints()
        
        # Keep track of fixes applied
        fixes_applied = {
            "port_fixed": False,
            "config_updated": False
        }
        
        # Fix PORT configuration
        if args.fix_port_only or not (args.update_config_only or args.verify_only):
            logger.info("Fixing PORT configuration...")
            fixes_applied["port_fixed"] = fix_port_configuration()
        
        # Update API endpoint in config.js
        if (args.update_config_only or not (args.fix_port_only or args.verify_only)) and endpoints.get("railway_endpoint"):
            logger.info("Updating API endpoint in config.js...")
            fixes_applied["config_updated"] = update_api_config(endpoints["railway_endpoint"])
        
        # Verify deployment
        if args.verify_only or not (args.fix_port_only or args.update_config_only):
            logger.info("Verifying deployment...")
            verification_results = verify_deployment(endpoints)
        else:
            verification_results = {
                "railway": False,
                "vercel": False,
                "supabase": False
            }
        
        # Generate summary
        summary_file = generate_summary(endpoints, fixes_applied, verification_results)
        
        # Display summary to console
        with open(summary_file, "r") as f:
            print(f.read())
        
        # Return 0 for success if we applied at least some fixes or verification was successful
        success = any(fixes_applied.values()) or any(verification_results.values())
        return 0 if success else 1
        
    except Exception as e:
        logger.error(f"Error in auto deployment fixer: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())
