#!/usr/bin/env python3
"""
Temporary File Cleanup Utility

This script identifies and removes temporary files that might cause 
deployment issues, particularly those with null bytes or backup files.
"""
import os
import sys
import argparse
import re
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

def is_temp_file(filename):
    """Check if a file is likely a temporary file."""
    temp_patterns = [
        r'temp_.*\.py$',        # Files starting with temp_
        r'.*_temp\.py$',        # Files ending with _temp
        r'.*\.py\.bak$',        # Python backup files
        r'fix_.*\.py$',         # Fix scripts
        r'.*_fixed\.py$',       # Fixed versions
        r'.*\.py~$',            # Backup files with tilde
        r'.*\.pyc$',            # Compiled Python files
        r'.*\.pyo$',            # Optimized Python files
        r'__pycache__',         # Python cache directory
    ]
    
    for pattern in temp_patterns:
        if re.match(pattern, filename):
            return True
    return False

def check_for_null_bytes(file_path):
    """Check if a file contains null bytes."""
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
        return b'\x00' in content
    except Exception:
        return False

def find_temp_files(directory, recursive=True, check_null_bytes=True):
    """
    Find temporary files that might be problematic for deployment.
    
    Args:
        directory: Directory to check
        recursive: Whether to check subdirectories
        check_null_bytes: Whether to check for null bytes
        
    Returns:
        List of problematic files
    """
    temp_files = []
    null_byte_files = []
    
    if recursive:
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, directory)
                
                if is_temp_file(file):
                    temp_files.append(rel_path)
                elif check_null_bytes and file.endswith('.py') and check_for_null_bytes(file_path):
                    null_byte_files.append(rel_path)
    else:
        for file in os.listdir(directory):
            file_path = os.path.join(directory, file)
            if os.path.isfile(file_path):
                if is_temp_file(file):
                    temp_files.append(file)
                elif check_null_bytes and file.endswith('.py') and check_for_null_bytes(file_path):
                    null_byte_files.append(file)
    
    return temp_files, null_byte_files

def main():
    parser = argparse.ArgumentParser(description='Find and clean up temporary files that might cause deployment issues.')
    parser.add_argument('--directory', '-d', default='.', help='Directory to check')
    parser.add_argument('--no-recursive', action='store_true', help='Do not check subdirectories')
    parser.add_argument('--delete', action='store_true', help='Delete the identified temporary files')
    parser.add_argument('--check-null-bytes', action='store_true', help='Also check for files with null bytes')
    
    args = parser.parse_args()
    
    print(f"{Fore.CYAN}=== LocalLift Temporary File Cleanup ==={Style.RESET_ALL}")
    
    temp_files, null_byte_files = find_temp_files(
        args.directory, 
        not args.no_recursive, 
        args.check_null_bytes
    )
    
    # Print findings
    if temp_files:
        print(f"\n{Fore.YELLOW}Found {len(temp_files)} temporary files:{Style.RESET_ALL}")
        for file in temp_files:
            print(f"  - {file}")
    else:
        print(f"\n{Fore.GREEN}No temporary files found.{Style.RESET_ALL}")
    
    if args.check_null_bytes and null_byte_files:
        print(f"\n{Fore.RED}Found {len(null_byte_files)} files with null bytes:{Style.RESET_ALL}")
        for file in null_byte_files:
            print(f"  - {file}")
    
    # Delete files if requested
    if args.delete and (temp_files or null_byte_files):
        confirmation = input(f"\n{Fore.YELLOW}Delete {len(temp_files) + len(null_byte_files)} files? (y/n): {Style.RESET_ALL}")
        if confirmation.lower() == 'y':
            deleted_count = 0
            for file in temp_files + null_byte_files:
                file_path = os.path.join(args.directory, file)
                try:
                    os.remove(file_path)
                    print(f"{Fore.GREEN}✓ Deleted: {file}{Style.RESET_ALL}")
                    deleted_count += 1
                except Exception as e:
                    print(f"{Fore.RED}✗ Failed to delete {file}: {e}{Style.RESET_ALL}")
            
            print(f"\n{Fore.GREEN}Successfully deleted {deleted_count} files.{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.YELLOW}No files were deleted.{Style.RESET_ALL}")
    
    # Return success if no problematic files found
    return 0 if not (temp_files or null_byte_files) else 1

if __name__ == "__main__":
    sys.exit(main())
