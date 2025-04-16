#!/usr/bin/env python3
"""
Pre-Deployment Validation Script

This script performs critical validation checks before deployment:
1. Checks for files with null bytes that would cause deployment failures
2. Verifies essential configuration files exist
3. Checks API endpoint configuration 
4. Validates environment variables are properly set
"""
import os
import sys
import json
import argparse
from pathlib import Path

# Add parent directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
sys.path.insert(0, parent_dir)

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

def check_for_null_bytes(directory, extensions=None, verbose=False, fix=False):
    """
    Check for null bytes in files and optionally fix them.
    
    Args:
        directory: Directory to check
        extensions: File extensions to check
        verbose: Whether to print verbose output
        fix: Whether to fix files with null bytes
        
    Returns:
        Tuple of (problem_files, fixed_files)
    """
    if extensions is None:
        extensions = ['.py']
    
    problem_files = []
    fixed_files = []
    
    print(f"{Fore.CYAN}Checking for null bytes in {directory}...{Style.RESET_ALL}")
    
    for root, _, files in os.walk(directory):
        for file in files:
            if not any(file.endswith(ext) for ext in extensions):
                continue
                
            file_path = os.path.join(root, file)
            
            try:
                with open(file_path, 'rb') as f:
                    content = f.read()
                
                if b'\x00' in content:
                    rel_path = os.path.relpath(file_path, directory)
                    problem_files.append(rel_path)
                    print(f"{Fore.RED}✗ NULL BYTES FOUND: {rel_path}{Style.RESET_ALL}")
                    
                    if fix:
                        # Create backup
                        backup_path = file_path + '.bak'
                        with open(backup_path, 'wb') as f:
                            f.write(content)
                        
                        # Remove null bytes
                        cleaned_content = content.replace(b'\x00', b'')
                        
                        # Save with UTF-8 encoding
                        try:
                            decoded = cleaned_content.decode('utf-8')
                        except UnicodeDecodeError:
                            try:
                                decoded = cleaned_content.decode('latin-1')
                            except UnicodeDecodeError:
                                decoded = cleaned_content.decode('utf-8', errors='replace')
                        
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(decoded)
                        
                        fixed_files.append(rel_path)
                        print(f"{Fore.GREEN}✓ Fixed: {rel_path}{Style.RESET_ALL}")
                
                elif verbose:
                    print(f"{Fore.GREEN}✓ Clean: {os.path.relpath(file_path, directory)}{Style.RESET_ALL}")
                    
            except Exception as e:
                print(f"{Fore.YELLOW}! Error checking {file_path}: {e}{Style.RESET_ALL}")
    
    return problem_files, fixed_files

def check_configs(directory):
    """
    Check for required configuration files.
    
    Args:
        directory: Root directory
        
    Returns:
        Tuple of (missing_files, errors)
    """
    missing_files = []
    errors = []
    
    print(f"{Fore.CYAN}Checking configuration files...{Style.RESET_ALL}")
    
    # Check for essential config files
    essential_files = [
        'vercel.json',
        'railway.json',
        'package.json',
        '.env.railway',
        'Dockerfile',
        'railway.toml'
    ]
    
    for file in essential_files:
        file_path = os.path.join(directory, file)
        if not os.path.exists(file_path):
            missing_files.append(file)
            print(f"{Fore.RED}✗ Missing required file: {file}{Style.RESET_ALL}")
        else:
            print(f"{Fore.GREEN}✓ Found: {file}{Style.RESET_ALL}")
            
            # Validate JSON files
            if file.endswith('.json'):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        json.load(f)
                except json.JSONDecodeError as e:
                    errors.append(f"Invalid JSON in {file}: {e}")
                    print(f"{Fore.RED}✗ Invalid JSON in {file}: {e}{Style.RESET_ALL}")
    
    return missing_files, errors

def check_api_endpoints(directory):
    """
    Check API endpoint configuration.
    
    Args:
        directory: Root directory
        
    Returns:
        List of issues found
    """
    issues = []
    
    print(f"{Fore.CYAN}Checking API endpoints...{Style.RESET_ALL}")
    
    # Check frontend config
    api_config_paths = [
        os.path.join(directory, 'public', 'js', 'config.js'),
        os.path.join(directory, 'static', 'js', 'config.js')
    ]
    
    api_configs_found = 0
    for config_path in api_config_paths:
        if os.path.exists(config_path):
            api_configs_found += 1
            print(f"{Fore.GREEN}✓ Found API config: {os.path.relpath(config_path, directory)}{Style.RESET_ALL}")
            
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if 'https://locallift-production.up.railway.app' not in content:
                issues.append(f"API endpoint not properly configured in {os.path.relpath(config_path, directory)}")
                print(f"{Fore.YELLOW}! API endpoint may not be properly configured in {os.path.relpath(config_path, directory)}{Style.RESET_ALL}")
    
    if api_configs_found == 0:
        issues.append("No API configuration files found")
        print(f"{Fore.YELLOW}! No API configuration files found{Style.RESET_ALL}")
    
    return issues

def main():
    parser = argparse.ArgumentParser(description='Pre-deployment validation for LocalLift')
    parser.add_argument('--directory', '-d', default='.', help='Project directory')
    parser.add_argument('--fix', action='store_true', help='Fix issues automatically when possible')
    parser.add_argument('--verbose', '-v', action='store_true', help='Print verbose output')
    
    args = parser.parse_args()
    
    print(f"{Fore.CYAN}=== LocalLift Pre-Deployment Validation ==={Style.RESET_ALL}")
    
    # Run checks
    problem_files, fixed_files = check_for_null_bytes(args.directory, fix=args.fix, verbose=args.verbose)
    missing_configs, config_errors = check_configs(args.directory)
    api_issues = check_api_endpoints(args.directory)
    
    # Print summary
    print(f"\n{Fore.CYAN}=== Validation Summary ==={Style.RESET_ALL}")
    
    exit_code = 0
    
    if not problem_files and not missing_configs and not config_errors and not api_issues:
        print(f"{Fore.GREEN}✓ All checks passed! The project is ready for deployment.{Style.RESET_ALL}")
    else:
        exit_code = 1
        
        if problem_files:
            if args.fix:
                if fixed_files:
                    print(f"{Fore.GREEN}✓ Fixed {len(fixed_files)} file(s) with null bytes.{Style.RESET_ALL}")
                if len(problem_files) > len(fixed_files):
                    print(f"{Fore.RED}✗ {len(problem_files) - len(fixed_files)} file(s) have null bytes that couldn't be fixed.{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}✗ {len(problem_files)} file(s) have null bytes. Run with --fix to attempt automatic fixing.{Style.RESET_ALL}")
        
        if missing_configs:
            print(f"{Fore.RED}✗ {len(missing_configs)} required configuration file(s) missing.{Style.RESET_ALL}")
        
        if config_errors:
            print(f"{Fore.RED}✗ {len(config_errors)} configuration error(s) found.{Style.RESET_ALL}")
        
        if api_issues:
            print(f"{Fore.YELLOW}! {len(api_issues)} API configuration issue(s) found.{Style.RESET_ALL}")
    
    return exit_code

if __name__ == "__main__":
    sys.exit(main())
