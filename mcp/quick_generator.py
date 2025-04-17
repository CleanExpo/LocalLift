#!/usr/bin/env python
"""
Quick Module Generator for LocalLift

A simplified tool to quickly generate module stubs based on configurations in module_configs.json.
This is a lightweight alternative to the full create_module.py for rapid prototyping.
"""
import os
import json
import sys
import argparse
from datetime import datetime

# Default paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "module_configs.json")
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)


def generate_module(module_key, config_path=CONFIG_PATH):
    """
    Generate a module stub based on configuration
    
    Args:
        module_key (str): Key of the module in the config file
        config_path (str): Path to the configuration file
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Load module configurations
        with open(config_path, "r") as f:
            data = json.load(f)
            modules = data.get("modules", {})
        
        # Check if module exists
        if module_key not in modules:
            print(f"❌ Module '{module_key}' not found in configuration.")
            return False
        
        # Get module details
        module = modules[module_key]
        description = module.get("description", "No description provided")
        role = module.get("role", "unknown")
        module_type = module.get("module_type", "generic")
        target_folder = module.get("target_folder", "")
        
        # Determine target directory
        if target_folder.startswith("/"):
            target_folder = target_folder[1:]  # Remove leading slash
        folder = os.path.join(PROJECT_ROOT, target_folder)
        
        # Create filename and full path
        filename = f"{module_type}_{role}.py"
        file_path = os.path.join(folder, filename)
        
        # Create directory if needed
        os.makedirs(folder, exist_ok=True)
        
        # Check if file already exists
        if os.path.exists(file_path):
            overwrite = input(f"File {file_path} already exists. Overwrite? (y/n): ")
            if overwrite.lower() != 'y':
                print("⏭️ Skipping file generation.")
                return False
        
        # Generate file content
        with open(file_path, "w") as f:
            f.write(f"#!/usr/bin/env python\n")
            f.write(f"# Auto-generated {module_type} for {role}\n")
            f.write(f"# Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# Description: {description}\n\n")
            
            f.write("def init():\n")
            f.write("    \"\"\"Initialize the module\"\"\"\n")
            f.write("    print(f\"Initializing {role} {module_type}...\")\n\n")
            
            f.write("def render():\n")
            f.write("    \"\"\"Render the module UI or response\"\"\"\n")
            f.write("    # TODO: implement rendering logic here\n")
            f.write("    return {\n")
            f.write("        \"status\": \"success\",\n")
            f.write("        \"module\": \"" + module_key + "\",\n")
            f.write("        \"data\": {}\n")
            f.write("    }\n\n")
            
            f.write("def process(data):\n")
            f.write("    \"\"\"Process incoming data\"\"\"\n")
            f.write("    # TODO: implement processing logic here\n")
            f.write("    return {\n")
            f.write("        \"status\": \"success\",\n")
            f.write("        \"message\": \"Data processed successfully\"\n")
            f.write("    }\n\n")
            
            f.write("# Run if script is used directly\n")
            f.write("if __name__ == \"__main__\":\n")
            f.write("    init()\n")
            f.write("    result = render()\n")
            f.write("    print(result)\n")
        
        print(f"✅ {filename} generated in {folder}")
        return True
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def list_modules(config_path=CONFIG_PATH):
    """
    List all available modules in the configuration
    
    Args:
        config_path (str): Path to the configuration file
    """
    try:
        # Load module configurations
        with open(config_path, "r") as f:
            data = json.load(f)
            modules = data.get("modules", {})
        
        if not modules:
            print("No modules found in configuration.")
            return
        
        print("\nAvailable modules:")
        for key, module in modules.items():
            role = module.get("role", "unknown")
            module_type = module.get("module_type", "generic")
            description = module.get("description", "No description").split(".")[0]  # Get first sentence
            
            print(f"  - {key}: {module_type} for {role} ({description})")
        
        print("\nUse: python quick_generator.py generate <module_key> to generate a module")
    
    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    """Main function for CLI interface"""
    parser = argparse.ArgumentParser(description="Quick Module Generator for LocalLift")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # List modules command
    list_parser = subparsers.add_parser("list", help="List available modules")
    
    # Generate module command
    generate_parser = subparsers.add_parser("generate", help="Generate a module stub")
    generate_parser.add_argument("module_key", help="Key of the module to generate")
    
    # Configuration file option
    parser.add_argument("--config", "-c", help="Path to the configuration file", default=CONFIG_PATH)
    
    args = parser.parse_args()
    
    if args.command == "list":
        list_modules(args.config)
    elif args.command == "generate":
        generate_module(args.module_key, args.config)
    else:
        if len(sys.argv) == 1:
            # Interactive mode
            list_modules(args.config)
            print("\nInteractive mode:")
            module_key = input("Enter module key (leave empty to exit): ")
            if module_key:
                generate_module(module_key, args.config)
        else:
            parser.print_help()


if __name__ == "__main__":
    main()
