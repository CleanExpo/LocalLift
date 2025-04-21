"""
Railway Health Checker

This script helps diagnose common issues with Railway deployments by:
1. Checking connection to the Railway service
2. Attempting to fetch logs from the Railway API (if available)
3. Testing different endpoint paths to find working routes
4. Checking for common configuration issues
"""

import requests
import sys
import json
import time
import os
from urllib.parse import urlparse

# Configuration
BASE_URL = "https://local-lift-production.up.railway.app"
ROUTES_TO_TEST = [
    "/",
    "/health",
    "/api",
    "/api/health",
    "/api/v1/health",
    "/ping",
    "/status",
    "/alive",
    "/ready"
]

def test_connection(url):
    """Test basic connectivity to the service"""
    print(f"\n🔍 Testing connection to {url}")
    try:
        response = requests.get(url, timeout=10)
        print(f"✅ Connected to {url}")
        print(f"   Status code: {response.status_code}")
        print(f"   Response headers: {json.dumps(dict(response.headers), indent=2)}")
        
        if response.status_code < 400:
            print(f"   Response body (truncated): {response.text[:200]}...")
        return response
    except requests.exceptions.ConnectionError:
        print(f"❌ Failed to connect to {url}")
        print("   The service might be down or the URL might be incorrect")
        return None
    except requests.exceptions.Timeout:
        print(f"❌ Connection to {url} timed out")
        print("   The service might be overloaded or not responding")
        return None
    except Exception as e:
        print(f"❌ Error connecting to {url}: {e}")
        return None

def test_routes():
    """Test all defined routes to see if any work"""
    print("\n🔍 Testing different API routes to find working endpoints")
    working_routes = []
    
    for route in ROUTES_TO_TEST:
        full_url = f"{BASE_URL}{route}"
        print(f"\nTesting route: {route}")
        try:
            response = requests.get(full_url, timeout=5)
            print(f"   Status code: {response.status_code}")
            
            if response.status_code < 400:
                print(f"   ✅ Route {route} works!")
                print(f"   Response (truncated): {response.text[:100]}...")
                working_routes.append(route)
            else:
                print(f"   ❌ Route {route} returned error code {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error testing route {route}: {e}")
    
    return working_routes

def analyze_railway_issues():
    """Analyze possible issues with Railway deployment"""
    print("\n🔍 Analyzing possible Railway deployment issues")
    
    # Check URL format
    parsed_url = urlparse(BASE_URL)
    if not parsed_url.scheme or not parsed_url.netloc:
        print("❌ Invalid URL format")
        return
    
    # Check if it's actually a Railway URL
    if "railway.app" not in parsed_url.netloc:
        print("⚠️ This doesn't appear to be a Railway URL")
    
    # Check for common Railway issues
    print("\nCommon Railway deployment issues to check:")
    print("1. ✅ Verify all environment variables are properly set in Railway dashboard")
    print("2. ✅ Check if your application is listening on the correct port (PORT env variable)")
    print("3. ✅ Look at Railway logs for startup errors")
    print("4. ✅ Make sure your application has the correct entrypoint (e.g., main.py)")
    print("5. ✅ Check if you've defined a /health endpoint in your application")
    print("6. ✅ Verify your application is actually starting up successfully")
    print("7. ✅ Make sure Railway domain is correctly configured")
    print("8. ✅ Check if your database connection is working")

def check_dns_resolution():
    """Check DNS resolution for the domain"""
    print("\n🔍 Checking DNS resolution")
    parsed_url = urlparse(BASE_URL)
    domain = parsed_url.netloc
    
    try:
        import socket
        ip = socket.gethostbyname(domain)
        print(f"✅ Domain {domain} resolves to IP {ip}")
    except socket.gaierror:
        print(f"❌ Could not resolve domain {domain}")
    except Exception as e:
        print(f"❌ Error checking DNS resolution: {e}")

def main():
    """Main function to run all checks"""
    print("=" * 50)
    print("Railway Deployment Health Checker")
    print("=" * 50)
    
    # Test basic connection
    response = test_connection(BASE_URL)
    
    # Test different routes
    working_routes = test_routes()
    
    # Check DNS resolution
    check_dns_resolution()
    
    # Analyze issues
    analyze_railway_issues()
    
    # Summary
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    
    if response and response.status_code < 400:
        print("✅ Base URL is accessible")
    else:
        print("❌ Base URL is not accessible")
    
    if working_routes:
        print(f"✅ Found {len(working_routes)} working routes:")
        for route in working_routes:
            print(f"   - {route}")
    else:
        print("❌ No working routes found")
    
    print("\n📋 Next steps:")
    print("1. Check the Railway dashboard logs for specific error messages")
    print("2. Verify your application has a proper health check endpoint")
    print("3. Make sure your application is listening on process.env.PORT")
    print("4. Review the environment variables in Railway")
    print("5. Try redeploying the application")
    print("\nRefer to DEPLOYMENT_TEST_RESULTS.md for more detailed troubleshooting steps.")

if __name__ == "__main__":
    main()
