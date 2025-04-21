#!/usr/bin/env python3
# MCP Endpoint Discovery Tool
# This script uses Model Context Protocol to identify working endpoints

import os
import sys
import json
import time
import logging
from datetime import datetime
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("mcp_endpoint_discovery")

# Constants
TIMEOUT = 10  # seconds
MCP_ENV_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "mcp-env")

# Ensure MCP_ENV_DIR exists
if not os.path.exists(MCP_ENV_DIR):
    os.makedirs(MCP_ENV_DIR)
    logger.info(f"Created MCP environment directory: {MCP_ENV_DIR}")

# Log file in MCP_ENV_DIR
log_file = os.path.join(MCP_ENV_DIR, f"endpoint_discovery_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

# Default endpoints to check
DEFAULT_ENDPOINTS = {
    "railway": [
        "https://locallift-production.up.railway.app",
        "https://locallift-backend.up.railway.app",
        "https://locallift-api.up.railway.app",
        "https://locallift.up.railway.app"
    ],
    "vercel": [
        "https://locallift.vercel.app",
        "https://locallift-frontend.vercel.app",
        "https://locallift-app.vercel.app"
    ],
    "supabase": [
        "https://supabase.co/dashboard/project/locallift",
        "https://locallift.supabase.co"
    ]
}

def check_endpoint(url, path="", timeout=TIMEOUT):
    """Check if an endpoint is responsive"""
    full_url = f"{url.rstrip('/')}/{path.lstrip('/')}"
    try:
        logger.info(f"Checking endpoint: {full_url}")
        start_time = time.time()
        response = requests.get(full_url, timeout=timeout)
        elapsed = time.time() - start_time
        status = response.status_code
        logger.info(f"Endpoint {full_url} returned {status} in {elapsed:.2f}s")
        return {
            "url": full_url,
            "status": status,
            "response_time": elapsed,
            "working": 200 <= status < 400,
            "content_type": response.headers.get("Content-Type", ""),
            "content_length": len(response.content)
        }
    except requests.RequestException as e:
        logger.warning(f"Failed to connect to {full_url}: {e}")
        return {
            "url": full_url,
            "status": 0,
            "response_time": 0,
            "working": False,
            "error": str(e)
        }

def discover_working_endpoints():
    """Find working endpoints for each service"""
    working_endpoints = {
        "railway": [],
        "vercel": [],
        "supabase": []
    }
    
    all_results = {
        "railway": [],
        "vercel": [],
        "supabase": []
    }

    # Check Railway endpoints
    logger.info("Checking Railway endpoints...")
    for url in DEFAULT_ENDPOINTS["railway"]:
        # Check multiple paths for Railway
        for path in ["", "api", "health", "api/health"]:
            result = check_endpoint(url, path)
            all_results["railway"].append(result)
            if result["working"] and result not in working_endpoints["railway"]:
                working_endpoints["railway"].append(result)
    
    # Check Vercel endpoints
    logger.info("Checking Vercel endpoints...")
    for url in DEFAULT_ENDPOINTS["vercel"]:
        result = check_endpoint(url)
        all_results["vercel"].append(result)
        if result["working"] and result not in working_endpoints["vercel"]:
            working_endpoints["vercel"].append(result)
    
    # Check Supabase connection (just placeholder URLs)
    logger.info("Checking Supabase endpoints...")
    for url in DEFAULT_ENDPOINTS["supabase"]:
        result = check_endpoint(url)
        all_results["supabase"].append(result)
        if result["working"] and result not in working_endpoints["supabase"]:
            working_endpoints["supabase"].append(result)
    
    return working_endpoints, all_results

def save_endpoints_config(working_endpoints):
    """Save working endpoints to a configuration file"""
    # Create simplified config for usage by other tools
    config = {
        "railway_endpoint": working_endpoints["railway"][0]["url"] if working_endpoints["railway"] else None,
        "vercel_endpoint": working_endpoints["vercel"][0]["url"] if working_endpoints["vercel"] else None,
        "supabase_endpoint": working_endpoints["supabase"][0]["url"] if working_endpoints["supabase"] else None
    }
    
    # Save as JSON
    config_file = os.path.join(MCP_ENV_DIR, "endpoints.json")
    with open(config_file, "w") as f:
        json.dump(config, f, indent=2)
    logger.info(f"Endpoint configuration saved to {config_file}")
    
    # Also create .env file for other tools
    env_file = os.path.join(MCP_ENV_DIR, ".env")
    with open(env_file, "w") as f:
        if config["railway_endpoint"]:
            f.write(f"API_ENDPOINT={config['railway_endpoint']}\n")
            f.write(f"HEALTH_ENDPOINT={config['railway_endpoint'].rstrip('/')}/health\n")
        if config["vercel_endpoint"]:
            f.write(f"FRONTEND_URL={config['vercel_endpoint']}\n")
        if config["supabase_endpoint"]:
            f.write(f"SUPABASE_URL={config['supabase_endpoint']}\n")
    logger.info(f"Environment variables saved to {env_file}")
    
    return config

def generate_summary(working_endpoints, all_results):
    """Generate a human-readable summary"""
    summary_file = os.path.join(MCP_ENV_DIR, "endpoint_discovery_summary.txt")
    
    with open(summary_file, "w") as f:
        f.write("=========================================\n")
        f.write(" LocalLift MCP Endpoint Discovery Report\n")
        f.write("=========================================\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("WORKING ENDPOINTS:\n")
        f.write("-----------------\n")
        
        # Railway
        if working_endpoints["railway"]:
            railway = working_endpoints["railway"][0]
            f.write(f"✅ RAILWAY API: {railway['url']} (Status: {railway['status']})\n")
        else:
            f.write("❌ RAILWAY API: No working endpoints found!\n")
        
        # Vercel
        if working_endpoints["vercel"]:
            vercel = working_endpoints["vercel"][0]
            f.write(f"✅ VERCEL FRONTEND: {vercel['url']} (Status: {vercel['status']})\n")
        else:
            f.write("❌ VERCEL FRONTEND: No working endpoints found!\n")
        
        # Supabase
        if working_endpoints["supabase"]:
            supabase = working_endpoints["supabase"][0]
            f.write(f"✅ SUPABASE DATABASE: {supabase['url']} (Status: {supabase['status']})\n")
        else:
            f.write("❌ SUPABASE DATABASE: No working endpoints found!\n")
        
        f.write("\nALL TESTED ENDPOINTS:\n")
        f.write("--------------------\n")
        
        for platform, results in all_results.items():
            f.write(f"\n[{platform.upper()}]\n")
            for result in results:
                status_icon = "✅" if result["working"] else "❌"
                f.write(f"{status_icon} {result['url']} (Status: {result['status']})\n")
        
        f.write("\n=========================================\n")
        f.write("For full details, see log file: " + os.path.basename(log_file) + "\n")
    
    logger.info(f"Summary report saved to {summary_file}")
    return summary_file

def main():
    """Main entry point for endpoint discovery"""
    
    logger.info("Starting MCP Endpoint Discovery")
    
    try:
        # Find working endpoints
        working_endpoints, all_results = discover_working_endpoints()
        
        # Save configuration
        config = save_endpoints_config(working_endpoints)
        
        # Generate summary
        summary_file = generate_summary(working_endpoints, all_results)
        
        # Display summary to console
        with open(summary_file, "r") as f:
            print(f.read())
        
        # Return 0 for success if we found at least some working endpoints
        has_working = any([len(endpoints) > 0 for _, endpoints in working_endpoints.items()])
        return 0 if has_working else 1
        
    except Exception as e:
        logger.error(f"Error in endpoint discovery: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())
