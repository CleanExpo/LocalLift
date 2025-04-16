#!/usr/bin/env python3
"""
Null Byte Detector for Python Files

This script scans all Python files in a directory (and its subdirectories) for null bytes,
which can cause syntax errors when deploying Python code. Files containing null bytes
need to be re-saved with proper UTF-8 encoding.
"""
import os
import sys
import argparse

# Add local lib directory to path for colorama
script_dir = os.path.dirname(os.path.abspath(__file__))
lib_dir = os.path.join(script_dir, 'lib')
if os.path.exists(lib_dir):
    sys.path.insert(0, lib_dir)

try:
    from colorama import init, Fore, Style
    # Initialize colorama for cross-platform colored terminal output
    init()
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

def check_files_for_null_bytes(directory, extensions=None, verbose=False):
    """
    Scan files for null bytes.
    
    Args:
        directory: Root directory to scan
        extensions: List of file extensions to check (default: ['.py'])
        verbose: Whether to print information about each file checked
        
    Returns:
        List of problematic file paths
    """
    if extensions is None:
        extensions = ['.py']
    
    problematic_files = []
    clean_files = []
    skipped_files = []
    
    print(f"{Fore.CYAN}Scanning directory: {directory}{Style.RESET_ALL}")
    
    for root, dirs, files in os.walk(directory):
        # Skip .git or other hidden directories
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for file in files:
            file_path = os.path.join(root, file)
            
            # Check if file has one of the target extensions
            if not any(file.endswith(ext) for ext in extensions):
                if verbose:
                    skipped_files.append(file_path)
                continue
                
            try:
                with open(file_path, 'rb') as f:
                    content = f.read()
                    if b'\x00' in content:
                        problematic_files.append(file_path)
                        print(f"{Fore.RED}✗ NULL BYTES FOUND: {file_path}{Style.RESET_ALL}")
                    else:
                        clean_files.append(file_path)
                        if verbose:
                            print(f"{Fore.GREEN}✓ Clean: {file_path}{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.YELLOW}! Error reading {file_path}: {e}{Style.RESET_ALL}")
    
    # Print summary
    print(f"\n{Fore.CYAN}=== Scan Summary ==={Style.RESET_ALL}")
    print(f"Total files checked: {len(clean_files) + len(problematic_files)}")
    print(f"Files with null bytes: {len(problematic_files)}")
    print(f"Clean files: {len(clean_files)}")
    
    if verbose:
        print(f"Skipped files: {len(skipped_files)}")
        
    # Return a list of problem files with relative paths
    return [os.path.relpath(file, directory) for file in problematic_files]

def main():
    parser = argparse.ArgumentParser(description='Scan files for null bytes that can cause deployment issues.')
    parser.add_argument('directory', nargs='?', default='.', 
                        help='Directory to scan (default: current directory)')
    parser.add_argument('-e', '--extensions', nargs='+', default=['.py'],
                        help='File extensions to check (default: .py)')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Print more detailed information')
    parser.add_argument('--all', action='store_true',
                        help='Check all files, regardless of extension')
    
    args = parser.parse_args()
    
    if args.all:
        extensions = None  # Check all files
    else:
        extensions = args.extensions
    
    problem_files = check_files_for_null_bytes(args.directory, extensions, args.verbose)
    
    if problem_files:
        print(f"\n{Fore.RED}Issues found! {len(problem_files)} files contain null bytes.{Style.RESET_ALL}")
        print(f"\n{Fore.YELLOW}To fix these issues:{Style.RESET_ALL}")
        print("1. Open each file in a text editor that supports UTF-8")
        print("2. Re-save the file with UTF-8 encoding (without BOM)")
        print("3. Verify the file was saved correctly by running this script again")
        return 1
    else:
        print(f"\n{Fore.GREEN}Success! No null bytes found in any files.{Style.RESET_ALL}")
        return 0

if __name__ == "__main__":
    sys.exit(main())
