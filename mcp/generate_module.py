#!/usr/bin/env python
"""
Module Generator for LocalLift

This script generates new modules for the LocalLift platform based on templates 
and configuration. It can be used to quickly scaffold new features, models, or API endpoints.
"""
import os
import sys
import json
import argparse
import re
import shutil
from datetime import datetime

# Default templates location
TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")


class ModuleGenerator:
    """
    Module generator for LocalLift application components
    """
    
    def __init__(self, module_type, name, options=None):
        """
        Initialize the module generator
        
        Args:
            module_type (str): Type of module to generate (feature, model, api, etc.)
            name (str): Name of the module
            options (dict): Additional options for generation
        """
        self.module_type = module_type
        self.name = name
        self.options = options or {}
        self.template_dir = os.path.join(TEMPLATES_DIR, module_type)
        self.target_dir = self._get_target_dir()
        
    def _get_target_dir(self):
        """Determine the target directory based on module type"""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        if self.module_type == "feature":
            return os.path.join(base_dir, "addons", self.name)
        elif self.module_type == "api":
            return os.path.join(base_dir, "backend", "api", self.name)
        elif self.module_type == "model":
            return os.path.join(base_dir, "core", "models", self.name)
        else:
            return os.path.join(base_dir, self.module_type, self.name)
    
    def generate(self):
        """Generate the module files from templates"""
        if not os.path.exists(self.template_dir):
            raise ValueError(f"Template directory for {self.module_type} not found")

        if not os.path.exists(self.target_dir):
            os.makedirs(self.target_dir)
            
        # Create required directories
        self._create_directories()
        
        # Generate files
        self._generate_files()
        
        return self.target_dir
    
    def _create_directories(self):
        """Create any required subdirectories"""
        template_structure_file = os.path.join(self.template_dir, "structure.json")
        
        if os.path.exists(template_structure_file):
            with open(template_structure_file, 'r') as f:
                structure = json.load(f)
                
            for directory in structure.get("directories", []):
                dir_path = os.path.join(self.target_dir, directory)
                if not os.path.exists(dir_path):
                    os.makedirs(dir_path)
    
    def _generate_files(self):
        """Generate files from templates"""
        template_files = [f for f in os.listdir(self.template_dir) 
                         if os.path.isfile(os.path.join(self.template_dir, f)) 
                         and f != "structure.json"]
        
        for template_file in template_files:
            # Skip hidden files and structure configuration
            if template_file.startswith('.'):
                continue
                
            template_path = os.path.join(self.template_dir, template_file)
            
            # Process the template filename for variables
            output_filename = self._process_template_string(template_file)
            output_path = os.path.join(self.target_dir, output_filename)
            
            # Read template content
            with open(template_path, 'r') as f:
                content = f.read()
            
            # Replace template variables in content
            content = self._process_template_string(content)
            
            # Write processed content to target file
            with open(output_path, 'w') as f:
                f.write(content)
    
    def _process_template_string(self, text):
        """
        Process a template string, replacing variables with their values
        
        Args:
            text (str): Template text with variables
            
        Returns:
            str: Processed text with variables replaced
        """
        # Create a dictionary of variables to replace
        variables = {
            "MODULE_NAME": self.name,
            "MODULE_TYPE": self.module_type,
            "YEAR": str(datetime.now().year),
            "DATE": datetime.now().strftime("%Y-%m-%d"),
            "TIMESTAMP": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "CLASS_NAME": self._to_class_name(self.name),
            "SNAKE_CASE": self._to_snake_case(self.name),
            "KEBAB_CASE": self._to_kebab_case(self.name),
            "CAMEL_CASE": self._to_camel_case(self.name),
        }
        
        # Add any custom options as variables
        for key, value in self.options.items():
            if isinstance(value, str):
                variables[key.upper()] = value
        
        # Replace variables in the text
        result = text
        for var_name, var_value in variables.items():
            result = result.replace(f"{{{{${var_name}$}}}}", var_value)
            
        return result
    
    @staticmethod
    def _to_class_name(name):
        """Convert a name to CamelCase class name"""
        parts = re.findall(r'[A-Za-z0-9]+', name)
        return ''.join(p.capitalize() for p in parts)
    
    @staticmethod
    def _to_snake_case(name):
        """Convert a name to snake_case"""
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    
    @staticmethod
    def _to_kebab_case(name):
        """Convert a name to kebab-case"""
        return ModuleGenerator._to_snake_case(name).replace('_', '-')
    
    @staticmethod
    def _to_camel_case(name):
        """Convert a name to camelCase"""
        parts = re.findall(r'[A-Za-z0-9]+', name.lower())
        return parts[0] + ''.join(p.capitalize() for p in parts[1:])


def create_template(template_type, name):
    """
    Create a new template for future module generation
    
    Args:
        template_type (str): Type of template to create
        name (str): Name of the template
    """
    template_dir = os.path.join(TEMPLATES_DIR, template_type)
    
    if not os.path.exists(template_dir):
        os.makedirs(template_dir)
    
    # Create basic structure file
    structure_file = os.path.join(template_dir, "structure.json")
    if not os.path.exists(structure_file):
        with open(structure_file, 'w') as f:
            json.dump({
                "name": template_type,
                "description": f"Template for {template_type} modules",
                "directories": ["tests"]
            }, f, indent=2)
    
    # Create a basic template file
    template_file = os.path.join(template_dir, f"{{{{$MODULE_NAME$}}}}.py")
    if not os.path.exists(template_file):
        with open(template_file, 'w') as f:
            f.write("""#!/usr/bin/env python
"""
f"""# {{{{$MODULE_NAME$}}}} module
# Generated on {{{{$TIMESTAMP$}}}}

class {{{{$CLASS_NAME$}}}}:
    \"\"\"
    {{{{$CLASS_NAME$}}}} class for the {{{{$MODULE_TYPE$}}}} module
    \"\"\"
    
    def __init__(self):
        \"\"\"Initialize the {{{{$CLASS_NAME$}}}} instance\"\"\"
        self.name = "{{{{$MODULE_NAME$}}}}"
    
    def get_name(self):
        \"\"\"Get the name of this module\"\"\"
        return self.name

""")


def main():
    """Main function for the module generator"""
    parser = argparse.ArgumentParser(description='Generate a module for LocalLift')
    parser.add_argument('action', choices=['generate', 'create-template'],
                        help='Action to perform')
    parser.add_argument('type', help='Type of module to generate or template to create')
    parser.add_argument('name', help='Name of the module or template')
    parser.add_argument('--options', '-o', help='Options in JSON format')
    
    args = parser.parse_args()
    
    try:
        # Parse options if provided
        options = json.loads(args.options) if args.options else {}
        
        if args.action == 'generate':
            generator = ModuleGenerator(args.type, args.name, options)
            target_dir = generator.generate()
            print(f"Module generated successfully in {target_dir}")
        elif args.action == 'create-template':
            create_template(args.type, args.name)
            print(f"Template '{args.type}' created successfully")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    
    return 0


if __name__ == "__main__":
    # Create templates directory if it doesn't exist
    if not os.path.exists(TEMPLATES_DIR):
        os.makedirs(TEMPLATES_DIR)
        
    sys.exit(main())
