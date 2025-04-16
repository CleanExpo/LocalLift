#!/usr/bin/env python3
"""
LocalLift Deployment Monitoring Tool

This script monitors the health and status of LocalLift deployments.
It checks both the Railway backend and Vercel frontend, providing
detailed reports on their status.
"""
import argparse
import json
import os
import sys
import time
from datetime import datetime
import subprocess
import requests
from pathlib import Path

# Optional colorama support
try:
    from colorama import init, Fore, Style
    init()  # Initialize colorama
    HAS_COLOR = True
except ImportError:
    # Create dummy color objects if colorama is not available
    class DummyColor:
        def __getattr__(self, name):
            return ""
    class DummyInit:
        def __call__(self, *args, **kwargs):
            pass
    Fore = DummyColor()
    Style = DummyColor()
    init = DummyInit()
    HAS_COLOR = False

# Default endpoints
DEFAULT_BACKEND_URL = "https://locallift-production.up.railway.app"
DEFAULT_FRONTEND_URL = "https://local-lift-frontend.vercel.app"

# Endpoints to check
ENDPOINTS = [
    # Backend health checks
    {"name": "API Health", "url": "{backend}/api/health", "type": "backend"},
    {"name": "API Version", "url": "{backend}/api/version", "type": "backend", "optional": True},
    
    # Frontend checks
    {"name": "Frontend", "url": "{frontend}", "type": "frontend"},
    {"name": "Frontend Config", "url": "{frontend}/config.js", "type": "frontend"},
    
    # API endpoints - mark as optional since they might require auth
    {"name": "API Users", "url": "{backend}/api/users", "type": "backend", "optional": True},
    {"name": "API Dashboard", "url": "{backend}/api/dashboard", "type": "backend", "optional": True},
]

def check_endpoint(url, name, optional=False):
    """Check if an endpoint is accessible"""
    try:
        start_time = time.time()
        response = requests.get(url, timeout=10)
        elapsed = time.time() - start_time
        
        if response.status_code < 400:
            status = "UP"
            color = Fore.GREEN
        else:
            status = f"DOWN ({response.status_code})"
            color = Fore.RED if not optional else Fore.YELLOW
            
        return {
            "name": name,
            "url": url,
            "status": status,
            "response_time": elapsed,
            "code": response.status_code,
            "color": color,
            "optional": optional
        }
    except requests.RequestException as e:
        return {
            "name": name,
            "url": url,
            "status": f"ERROR: {str(e)[:50]}...",
            "response_time": 0,
            "code": 0,
            "color": Fore.RED if not optional else Fore.YELLOW,
            "optional": optional
        }

def check_deployment(backend_url, frontend_url, export_json=False, continuous=False, interval=300):
    """Check the status of all deployment endpoints"""
    while True:
        results = []
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"{Fore.CYAN}=== LocalLift Deployment Status Check - {timestamp} ==={Style.RESET_ALL}")
        print(f"{Fore.CYAN}Backend: {backend_url}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Frontend: {frontend_url}{Style.RESET_ALL}")
        print("")
        
        for endpoint in ENDPOINTS:
            url = endpoint["url"].format(backend=backend_url, frontend=frontend_url)
            result = check_endpoint(url, endpoint["name"], endpoint.get("optional", False))
            results.append(result)
            
            status_color = result["color"]
            print(f"{status_color}{result['name']}: {result['status']} - {result['url']} ({result['response_time']:.2f}s){Style.RESET_ALL}")
        
        # Overall status
        critical_endpoints = [r for r in results if not r["optional"]]
        if all(r["code"] < 400 for r in critical_endpoints):
            overall_status = f"{Fore.GREEN}HEALTHY{Style.RESET_ALL}"
        else:
            overall_status = f"{Fore.RED}UNHEALTHY{Style.RESET_ALL}"
            
        print("")
        print(f"Overall System Status: {overall_status}")
        
        # Export to JSON if requested
        if export_json:
            export_data = {
                "timestamp": timestamp,
                "backend_url": backend_url,
                "frontend_url": frontend_url,
                "overall_status": "HEALTHY" if overall_status == f"{Fore.GREEN}HEALTHY{Style.RESET_ALL}" else "UNHEALTHY",
                "endpoints": [{
                    "name": r["name"],
                    "url": r["url"],
                    "status": r["status"],
                    "response_time": r["response_time"],
                    "code": r["code"],
                    "optional": r["optional"]
                } for r in results]
            }
            
            filename = f"deployment_status_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, "w") as f:
                json.dump(export_data, f, indent=2)
                
            print(f"Status exported to {filename}")
        
        if not continuous:
            break
            
        print(f"Next check in {interval} seconds...")
        time.sleep(interval)

def main():
    parser = argparse.ArgumentParser(description='Monitor LocalLift deployments')
    parser.add_argument('--backend', default=DEFAULT_BACKEND_URL, help='Backend URL')
    parser.add_argument('--frontend', default=DEFAULT_FRONTEND_URL, help='Frontend URL')
    parser.add_argument('--export', action='store_true', help='Export results to JSON')
    parser.add_argument('--continuous', '-c', action='store_true', help='Run continuously')
    parser.add_argument('--interval', '-i', type=int, default=300, help='Check interval in seconds (for continuous mode)')
    
    args = parser.parse_args()
    
    try:
        check_deployment(
            args.backend, 
            args.frontend, 
            args.export, 
            args.continuous, 
            args.interval
        )
        return 0
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user")
        return 0
    except Exception as e:
        print(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
