"""
Supabase Connection Test Script

This script tests the connection to your Supabase database and helps diagnose connection issues.
It will try both direct PostgreSQL connection and API connection to identify the source of the problem.
"""

import os
import sys
import socket
import time
from urllib.parse import urlparse

try:
    import psycopg2
    import requests
    from psycopg2 import sql
except ImportError:
    print("Required packages not found. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "psycopg2-binary", "requests"])
    import psycopg2
    import requests
    from psycopg2 import sql

# Configuration - Edit these values
SUPABASE_DB_HOST = "52.0.91.163"
SUPABASE_DB_PORT = "5432"
SUPABASE_DB_USER = "postgres"
SUPABASE_DB_PASSWORD = "Sanctuary2025!@"
SUPABASE_URL = "https://rsooolwhapkkkwbmybdb.supabase.co"  # Update with your project URL
SUPABASE_SERVICE_ROLE_KEY = ""  # Add your service role key if available

# -----------------------------------------
# Database connection tests
# -----------------------------------------

def test_direct_connection():
    """Test direct PostgreSQL connection"""
    print("\n--- Testing Direct PostgreSQL Connection ---")
    
    # Test DNS resolution
    try:
        print(f"Resolving hostname {SUPABASE_DB_HOST}...")
        ip_address = socket.gethostbyname(SUPABASE_DB_HOST)
        print(f"✓ Hostname resolved to {ip_address}")
    except socket.gaierror as e:
        print(f"✗ Failed to resolve hostname: {e}")
        print("  This could indicate a DNS issue or an incorrect hostname.")
        
    # Test TCP connection
    try:
        print(f"Testing TCP connection to {SUPABASE_DB_HOST}:{SUPABASE_DB_PORT}...")
        start_time = time.time()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        s.connect((SUPABASE_DB_HOST, int(SUPABASE_DB_PORT)))
        s.close()
        duration = time.time() - start_time
        print(f"✓ Successfully established TCP connection (took {duration:.2f} seconds)")
    except socket.error as e:
        print(f"✗ Failed to establish TCP connection: {e}")
        print("  This indicates a network connectivity issue or firewall restriction.")

    # Try PostgreSQL connection with various options
    connection_variants = [
        {
            "name": "Default connection",
            "params": {
                "host": SUPABASE_DB_HOST,
                "port": SUPABASE_DB_PORT, 
                "dbname": "postgres",
                "user": SUPABASE_DB_USER,
                "password": SUPABASE_DB_PASSWORD,
                "connect_timeout": 10
            }
        },
        {
            "name": "Connection with sslmode=require",
            "params": {
                "host": SUPABASE_DB_HOST,
                "port": SUPABASE_DB_PORT, 
                "dbname": "postgres",
                "user": SUPABASE_DB_USER,
                "password": SUPABASE_DB_PASSWORD,
                "sslmode": "require",
                "connect_timeout": 10
            }
        },
        {
            "name": "Connection with IPv4 option",
            "params": {
                "host": SUPABASE_DB_HOST,
                "port": SUPABASE_DB_PORT, 
                "dbname": "postgres",
                "user": SUPABASE_DB_USER,
                "password": SUPABASE_DB_PASSWORD,
                "options": "-c AddressFamily=inet",
                "connect_timeout": 10
            }
        }
    ]
    
    for variant in connection_variants:
        print(f"\nTrying {variant['name']}...")
        try:
            start_time = time.time()
            conn = psycopg2.connect(**variant['params'])
            duration = time.time() - start_time
            
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            
            print(f"✓ Connection successful! (took {duration:.2f} seconds)")
            print(f"  PostgreSQL version: {version}")
            
            # Test access to user_roles table
            try:
                cursor.execute("SELECT COUNT(*) FROM public.user_roles;")
                count = cursor.fetchone()[0]
                print(f"✓ Successfully accessed user_roles table (contains {count} records)")
            except Exception as e:
                print(f"✗ Could not access user_roles table: {e}")
            
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            print(f"✗ Connection failed: {e}")
    
    print("\n❌ All direct PostgreSQL connection attempts failed")
    return False

def test_api_connection():
    """Test Supabase API connection"""
    print("\n--- Testing Supabase API Connection ---")
    
    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        print("✗ Supabase URL or Service Role Key not provided. Skipping API test.")
        return False

    try:
        parsed_url = urlparse(SUPABASE_URL)
        if not parsed_url.scheme or not parsed_url.netloc:
            print(f"✗ Invalid Supabase URL format: {SUPABASE_URL}")
            return False
            
        # Test API reachability
        print(f"Testing connection to {SUPABASE_URL}...")
        headers = {
            "apikey": SUPABASE_SERVICE_ROLE_KEY,
            "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}"
        }
        
        # Get a health check or similar endpoint response
        response = requests.get(f"{SUPABASE_URL}/rest/v1/", headers=headers)
        if response.status_code < 300:
            print(f"✓ Successfully connected to Supabase API (status code: {response.status_code})")
            
            # Test table access if health check succeeds
            table_response = requests.get(f"{SUPABASE_URL}/rest/v1/user_roles?select=count", headers=headers)
            if table_response.status_code < 300:
                print(f"✓ Successfully accessed user_roles table via API (status code: {table_response.status_code})")
                return True
            else:
                print(f"✗ Failed to access user_roles table via API (status code: {table_response.status_code})")
                print(f"  Response: {table_response.text}")
        else:
            print(f"✗ Failed to connect to Supabase API (status code: {response.status_code})")
            print(f"  Response: {response.text}")
    except Exception as e:
        print(f"✗ API connection test failed: {e}")
    
    print("\n❌ Supabase API connection test failed")
    return False

# -----------------------------------------
# Diagnostics
# -----------------------------------------

def print_summary(direct_success, api_success):
    """Print summary of test results and recommendations"""
    print("\n=========================================")
    print("          CONNECTION TEST SUMMARY        ")
    print("=========================================")
    
    if direct_success:
        print("✅ Direct PostgreSQL connection: SUCCESSFUL")
    else:
        print("❌ Direct PostgreSQL connection: FAILED")
    
    if api_success:
        print("✅ Supabase API connection: SUCCESSFUL")
    else:
        print("❌ Supabase API connection: FAILED")
    
    print("\n--- DIAGNOSIS ---")
    
    if direct_success and api_success:
        print("📊 All connections are working properly.")
        print("   - Update your Railway environment variables")
        print("   - Redeploy the application")
        print("   - Your connection issue should be resolved")
    elif direct_success and not api_success:
        print("📊 Direct PostgreSQL connection works, but API connection fails.")
        print("   - Check your SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY")
        print("   - Update these variables in Railway")
        print("   - Configure your application to use direct PostgreSQL connection")
    elif not direct_success and api_success:
        print("📊 API connection works, but direct PostgreSQL connection fails.")
        print("   - Update connection.py to use the Supabase API client instead of SQLAlchemy")
        print("   - Make sure SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are set in Railway")
        print("   - This approach will bypass PostgreSQL connection issues")
    else:
        print("📊 All connection methods failed.")
        print("   - Verify the Supabase project is active")
        print("   - Check if there are IP allow lists in Supabase that might be blocking connections")
        print("   - Confirm your database credentials and connection parameters")
        print("   - Consider contacting Supabase support for assistance")

# -----------------------------------------
# Main execution
# -----------------------------------------

def main():
    print("=========================================")
    print("       SUPABASE CONNECTION TEST          ")
    print("=========================================")
    print(f"Database Host: {SUPABASE_DB_HOST}")
    print(f"Database Port: {SUPABASE_DB_PORT}")
    print(f"Database User: {SUPABASE_DB_USER}")
    
    direct_success = test_direct_connection()
    api_success = test_api_connection()
    
    print_summary(direct_success, api_success)

if __name__ == "__main__":
    main()
