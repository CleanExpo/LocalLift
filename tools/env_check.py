#!/usr/bin/env python
"""
Environment Variables Checker for LocalLift

This script checks if all the required environment variables are set and valid.
"""

import os
import re
import sys
from pathlib import Path
from datetime import datetime

# ANSI color codes for colored output
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
BOLD = "\033[1m"
RESET = "\033[0m"

def print_colored(text, color):
    """Print colored text"""
    print(f"{color}{text}{RESET}")

def print_header(text):
    """Print a header"""
    print(f"\n{BLUE}{BOLD}{'=' * 50}{RESET}")
    print(f"{BLUE}{BOLD}{text.center(50)}{RESET}")
    print(f"{BLUE}{BOLD}{'=' * 50}{RESET}\n")

def print_result(name, status, message=None):
    """Print check result"""
    if status:
        print(f"{GREEN}✅ {name}: {RESET}{message}" if message else f"{GREEN}✅ {name}{RESET}")
    else:
        print(f"{RED}❌ {name}: {RESET}{message}" if message else f"{RED}❌ {name}{RESET}")

def validate_url(url):
    """Validate URL format"""
    pattern = re.compile(r'^https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+')
    return bool(pattern.match(url))

def validate_jwt(token):
    """Simple validation for JWT token format"""
    pattern = re.compile(r'^[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*$')
    return bool(pattern.match(token))

def validate_sendgrid_key(key):
    """Validate SendGrid API key format"""
    return key.startswith('SG.')

def validate_uuid(uuid_str):
    """Validate UUID format"""
    pattern = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')
    return bool(pattern.match(uuid_str.lower()))

def check_env_variables():
    """Check environment variables"""
    # Load .env file
    env_path = Path('.env')
    if not env_path.exists():
        print_colored("ERROR: .env file not found in the current directory!", RED)
        return False
    
    # Read .env file and parse variables
    env_vars = {}
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            key, value = line.split('=', 1)
            env_vars[key.strip()] = value.strip()
    
    # Required variables groups
    supabase_vars = [
        ('SUPABASE_URL', validate_url),
        ('SUPABASE_ANON_KEY', validate_jwt),
        ('SUPABASE_SERVICE_ROLE_KEY', validate_jwt),
        ('SUPABASE_JWT_SECRET', None),
        ('SUPABASE_PROJECT_ID', None)
    ]
    
    email_vars = [
        ('SENDGRID_API_KEY', validate_sendgrid_key),
        ('EMAIL_FROM', None),
        ('EMAIL_NAME', None)
    ]
    
    infra_vars = [
        ('RAILWAY_PROJECT_ID', validate_uuid),
    ]
    
    # Check Supabase variables
    print_header("Supabase Configuration")
    supabase_ok = True
    for name, validator in supabase_vars:
        if name not in env_vars:
            print_result(name, False, "Missing")
            supabase_ok = False
            continue
        
        value = env_vars[name]
        if validator and not validator(value):
            print_result(name, False, f"Invalid format: {value[:10]}...")
            supabase_ok = False
        else:
            print_result(name, True, f"{'*' * min(10, len(value))}{'...' if len(value) > 10 else ''}")
    
    # Check Email variables
    print_header("Email Configuration")
    email_ok = True
    for name, validator in email_vars:
        if name not in env_vars:
            print_result(name, False, "Missing")
            email_ok = False
            continue
        
        value = env_vars[name]
        if validator and not validator(value):
            print_result(name, False, f"Invalid format: {value[:10]}...")
            email_ok = False
        else:
            print_result(name, True, f"{'*' * min(10, len(value))}{'...' if len(value) > 10 else ''}")
    
    # Check Infrastructure variables
    print_header("Infrastructure Configuration")
    infra_ok = True
    for name, validator in infra_vars:
        if name not in env_vars:
            print_result(name, False, "Missing")
            infra_ok = False
            continue
        
        value = env_vars[name]
        if validator and not validator(value):
            print_result(name, False, f"Invalid format: {value}")
            infra_ok = False
        else:
            print_result(name, True, value)
    
    # Summary
    print_header("Environment Check Summary")
    
    all_ok = supabase_ok and email_ok and infra_ok
    if all_ok:
        print_colored("✅ All environment variables are set and valid!", GREEN)
    else:
        print_colored("❌ Some environment variables are missing or invalid!", RED)
    
    print(f"\nSupabase: {'🟢 OK' if supabase_ok else '🔴 Issues'}")
    print(f"Email: {'🟢 OK' if email_ok else '🔴 Issues'}")
    print(f"Infrastructure: {'🟢 OK' if infra_ok else '🔴 Issues'}")
    
    print(f"\nChecked at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return all_ok

if __name__ == "__main__":
    print_header("LocalLift Environment Variables Check")
    success = check_env_variables()
    sys.exit(0 if success else 1)
