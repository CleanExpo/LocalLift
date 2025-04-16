#!/usr/bin/env python3
"""
Null Byte Fixer for Python Files

This script scans for null bytes in specified files and resaves them with proper UTF-8 encoding.
It removes null bytes in the process to prevent SyntaxError during deployment.
"""
import os
import sys
import argparse
import shutil
from pathlib import Path

def fix_file_encoding(file_path, backup=True, verbose=False):
    """
    Fix file encoding by removing null bytes and saving with UTF-8.
    
    Args:
        file_path: Path to the file to fix
        backup: Whether to create a backup of the original file
        verbose: Whether to print detailed information
        
    Returns:
        bool: Success status
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        return False
    
    # Create backup if requested
    if backup:
        backup_path = file_path.with_suffix(file_path.suffix + '.bak')
        shutil.copy2(file_path, backup_path)
        if verbose:
            print(f"Created backup: {backup_path}")
    
    try:
        # Read file in binary mode to preserve as much as possible
        with open(file_path, 'rb') as f:
            content = f.read()
        
        # Check if there are null bytes
        if b'\x00' not in content:
            print(f"No null bytes found in {file_path}, already clean.")
            return True
        
        # Remove null bytes
        cleaned_content = content.replace(b'\x00', b'')
        
        # Try to decode and re-encode to ensure valid UTF-8
        try:
            # Try to decode as UTF-8 first (might be already UTF-8 with null bytes)
            decoded = cleaned_content.decode('utf-8')
        except UnicodeDecodeError:
            # If that fails, try latin-1 which accepts any byte value
            try:
                decoded = cleaned_content.decode('latin-1')
            except UnicodeDecodeError:
                # If even that fails, just replace invalid characters
                decoded = cleaned_content.decode('utf-8', errors='replace')
        
        # Write back with proper UTF-8 encoding
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(decoded)
        
        print(f"✓ Fixed encoding for: {file_path}")
        return True
        
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Fix files with null bytes by removing them and saving with UTF-8 encoding.')
    parser.add_argument('files', nargs='+', help='Files to fix')
    parser.add_argument('--no-backup', action='store_true', help='Do not create backup files')
    parser.add_argument('-v', '--verbose', action='store_true', help='Print more detailed information')
    
    args = parser.parse_args()
    
    success_count = 0
    fail_count = 0
    
    for file_path in args.files:
        if fix_file_encoding(file_path, not args.no_backup, args.verbose):
            success_count += 1
        else:
            fail_count += 1
    
    print(f"\nFixed {success_count} file(s), failed to fix {fail_count} file(s).")
    
    return 0 if fail_count == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
