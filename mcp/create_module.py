#!/usr/bin/env python
"""
Module Creator for LocalLift

This script creates modules based on configurations defined in module_configs.json.
It generates all required files, directories, and boilerplate code for the specified module.
"""
import os
import sys
import json
import argparse
import shutil
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("create_module")

# Default paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "module_configs.json")
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)


class ModuleCreator:
    """Creates modules based on predefined configurations"""
    
    def __init__(self, config_path: str = CONFIG_PATH):
        """
        Initialize the module creator
        
        Args:
            config_path (str): Path to the module configuration JSON file
        """
        self.config_path = config_path
        self.configs = {}
        self._load_configs()
        
    def _load_configs(self):
        """Load the module configurations from the JSON file"""
        try:
            with open(self.config_path, 'r') as f:
                data = json.load(f)
                
            self.configs = data.get("modules", {})
            metadata = data.get("metadata", {})
                
            logger.info(f"Loaded module configurations version {metadata.get('version', 'unknown')}")
            logger.info(f"Found {len(self.configs)} module configurations")
        except Exception as e:
            logger.error(f"Failed to load module configurations: {e}")
            raise
    
    def list_modules(self) -> List[Dict[str, Any]]:
        """
        List available module configurations
        
        Returns:
            List[Dict[str, Any]]: List of module configurations
        """
        return [
            {"id": module_id, "description": config.get("description", ""), "type": config.get("module_type", "")} 
            for module_id, config in self.configs.items()
        ]
    
    def get_module_config(self, module_id: str) -> Dict[str, Any]:
        """
        Get a module configuration by ID
        
        Args:
            module_id (str): ID of the module configuration
            
        Returns:
            Dict[str, Any]: Module configuration
            
        Raises:
            ValueError: If the module ID is not found
        """
        if module_id not in self.configs:
            raise ValueError(f"Module configuration '{module_id}' not found")
        
        return self.configs[module_id]
    
    def create_module(self, module_id: str, options: Dict[str, Any] = None) -> str:
        """
        Create a module based on a configuration
        
        Args:
            module_id (str): ID of the module configuration
            options (Dict[str, Any], optional): Additional options for creation
            
        Returns:
            str: Path to the created module
            
        Raises:
            ValueError: If the module ID is not found
        """
        config = self.get_module_config(module_id)
        opt = options or {}
        
        # Get the target folder
        target_folder = config.get("target_folder", "")
        if not target_folder:
            raise ValueError(f"Module '{module_id}' does not have a target_folder defined")
        
        # Convert relative path to absolute path
        if target_folder.startswith("/"):
            target_folder = target_folder[1:]  # Remove leading slash
        target_path = os.path.join(PROJECT_ROOT, target_folder)
        
        # Create the target directory if it doesn't exist
        os.makedirs(target_path, exist_ok=True)
        logger.info(f"Creating module '{module_id}' in {target_path}")
        
        # Create each template file
        templates = config.get("templates", [])
        for template in templates:
            self._create_template_file(module_id, template, target_path, config, opt)
        
        # Generate model files if specified
        models = config.get("models", [])
        for model in models:
            self._create_model_file(module_id, model, target_path, config, opt)
        
        # Create __init__.py to make it a proper package
        init_path = os.path.join(target_path, "__init__.py")
        if not os.path.exists(init_path):
            with open(init_path, 'w') as f:
                f.write(f'"""\n{config.get("description", "")}\n"""\n\n')
        
        return target_path
    
    def _create_template_file(
        self, 
        module_id: str, 
        template: Dict[str, Any], 
        target_path: str,
        config: Dict[str, Any],
        options: Dict[str, Any]
    ):
        """
        Create a template file for a module
        
        Args:
            module_id (str): ID of the module
            template (Dict[str, Any]): Template configuration
            target_path (str): Base path for the module
            config (Dict[str, Any]): Module configuration
            options (Dict[str, Any]): Additional options
        """
        template_path = template.get("path", "")
        if not template_path:
            logger.warning(f"Template for '{module_id}' has no path defined, skipping")
            return
        
        description = template.get("description", "")
        file_path = os.path.join(target_path, template_path)
        
        # Create directories if they don't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Check for existing files
        if os.path.exists(file_path) and not options.get("overwrite", False):
            logger.warning(f"File {file_path} already exists, skipping (use --overwrite to force)")
            return
        
        # Determine the template content based on the file extension
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".py":
            content = self._generate_python_template(module_id, template, config)
        elif ext == ".html":
            content = self._generate_html_template(module_id, template, config)
        elif ext == ".js":
            content = self._generate_js_template(module_id, template, config)
        else:
            content = f"# {description}\n# Generated for {module_id} module\n"
        
        # Write the content to the file
        with open(file_path, 'w') as f:
            f.write(content)
        
        logger.info(f"Created template file {file_path}")
    
    def _create_model_file(
        self, 
        module_id: str, 
        model: Dict[str, Any], 
        target_path: str,
        config: Dict[str, Any],
        options: Dict[str, Any]
    ):
        """
        Create a model file for a module
        
        Args:
            module_id (str): ID of the module
            model (Dict[str, Any]): Model configuration
            target_path (str): Base path for the module
            config (Dict[str, Any]): Module configuration
            options (Dict[str, Any]): Additional options
        """
        model_name = model.get("name", "")
        if not model_name:
            logger.warning(f"Model for '{module_id}' has no name defined, skipping")
            return
        
        # Create models directory if it doesn't exist
        models_dir = os.path.join(target_path, "models")
        os.makedirs(models_dir, exist_ok=True)
        
        # Create __init__.py in models directory
        init_path = os.path.join(models_dir, "__init__.py")
        if not os.path.exists(init_path):
            with open(init_path, 'w') as f:
                f.write(f'"""\nModels for {module_id} module\n"""\n\n')
        
        # Create the model file
        model_path = os.path.join(models_dir, f"{self._to_snake_case(model_name)}.py")
        
        # Check for existing files
        if os.path.exists(model_path) and not options.get("overwrite", False):
            logger.warning(f"File {model_path} already exists, skipping (use --overwrite to force)")
            return
        
        # Generate the model content
        content = self._generate_model_template(model_name, model, config)
        
        # Write the content to the file
        with open(model_path, 'w') as f:
            f.write(content)
        
        logger.info(f"Created model file {model_path}")
        
        # Update __init__.py to import the model
        with open(init_path, 'a') as f:
            model_import = f"from .{self._to_snake_case(model_name)} import {model_name}\n"
            f.write(model_import)
    
    def _generate_python_template(
        self, 
        module_id: str, 
        template: Dict[str, Any], 
        config: Dict[str, Any]
    ) -> str:
        """
        Generate a Python template file content
        
        Args:
            module_id (str): ID of the module
            template (Dict[str, Any]): Template configuration
            config (Dict[str, Any]): Module configuration
            
        Returns:
            str: Template content
        """
        description = template.get("description", "")
        template_path = template.get("path", "")
        
        # Basic Python file structure
        content = f'''"""
{description}

This file is part of the {module_id} module for LocalLift.
Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

# Create router
router = APIRouter(
    prefix="/{module_id}",
    tags=["{module_id}"],
    responses={{404: {{"description": "Not found"}}}}
)

'''
        
        # Add appropriate content based on the file path
        if "api" in template_path:
            content += self._generate_api_content(module_id, template, config)
        
        return content
    
    def _generate_api_content(
        self, 
        module_id: str, 
        template: Dict[str, Any], 
        config: Dict[str, Any]
    ) -> str:
        """
        Generate API-specific Python content
        
        Args:
            module_id (str): ID of the module
            template (Dict[str, Any]): Template configuration
            config (Dict[str, Any]): Module configuration
            
        Returns:
            str: API content
        """
        # Import dependencies
        dependencies = config.get("dependencies", [])
        imports = ""
        for dep in dependencies:
            imports += f"from {dep} import models as {dep.split('.')[-1]}_models\n"
        
        # Generate models
        models = config.get("models", [])
        model_imports = ""
        if models:
            model_imports = f"from ..models import {', '.join([m.get('name', '') for m in models])}\n"
        
        # Generate basic route handlers
        content = f'''
{imports}
{model_imports}

# Data models
class {self._to_class_name(module_id)}Request(BaseModel):
    """Request model for {module_id}"""
    user_id: str
    # Add other fields as needed

class {self._to_class_name(module_id)}Response(BaseModel):
    """Response model for {module_id}"""
    status: str
    data: Dict[str, Any]
    # Add other fields as needed


@router.get("/")
async def get_{self._to_snake_case(module_id)}():
    """
    Get {module_id} data
    """
    return {{
        "status": "success",
        "message": "{module_id} endpoint"
    }}


@router.post("/", response_model={self._to_class_name(module_id)}Response)
async def create_{self._to_snake_case(module_id)}(request: {self._to_class_name(module_id)}Request):
    """
    Create {module_id} data
    """
    # Implement your logic here
    
    return {{
        "status": "success",
        "data": {{"request": request.dict()}}
    }}
'''
        
        return content
    
    def _generate_html_template(
        self, 
        module_id: str, 
        template: Dict[str, Any], 
        config: Dict[str, Any]
    ) -> str:
        """
        Generate an HTML template file content
        
        Args:
            module_id (str): ID of the module
            template (Dict[str, Any]): Template configuration
            config (Dict[str, Any]): Module configuration
            
        Returns:
            str: Template content
        """
        description = template.get("description", "")
        role = config.get("role", "")
        module_type = config.get("module_type", "")
        
        content = f'''{% extends "base.html" %}

{% block title %}{self._to_title_case(module_id)} - LocalLift{% endblock %}

{% block head %}
<!-- Additional head content for {module_id} -->
{% endblock %}

{% block content %}
<div class="container mx-auto px-4 py-6">
    <h1 class="text-3xl font-display font-bold mb-6">{self._to_title_case(module_id)}</h1>
    
    <!-- {description} -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <!-- Sidebar -->
        <div class="md:col-span-1">
            <div class="card mb-6">
                <h2 class="text-xl font-semibold mb-3">Navigation</h2>
                <nav class="space-y-2">
                    <a href="#" class="block text-primary-600 hover:text-primary-800">Dashboard</a>
                    <a href="#" class="block text-gray-700 hover:text-primary-600">Reports</a>
                    <a href="#" class="block text-gray-700 hover:text-primary-600">Settings</a>
                </nav>
            </div>
        </div>
        
        <!-- Main content -->
        <div class="md:col-span-2">
            <div class="card mb-6">
                <h2 class="text-xl font-semibold mb-4">Overview</h2>
                <p class="text-gray-700 mb-4">
                    Welcome to the {self._to_title_case(module_id)} for {role} users. 
                    This {module_type} provides tools for managing your data.
                </p>
                
                <!-- Add content specific to this module -->
                <div id="{self._to_kebab_case(module_id)}-content" class="mt-6">
                    <!-- Content will be loaded here -->
                    <div class="animate-pulse">
                        <div class="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
                        <div class="h-4 bg-gray-200 rounded w-1/2 mb-4"></div>
                        <div class="h-4 bg-gray-200 rounded w-5/6 mb-4"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<!-- JavaScript for {module_id} -->
<script src="{{ url_for('static', path='js/{self._to_snake_case(module_id)}.js') }}"></script>
{% endblock %}
'''
        
        return content
    
    def _generate_js_template(
        self, 
        module_id: str, 
        template: Dict[str, Any], 
        config: Dict[str, Any]
    ) -> str:
        """
        Generate a JavaScript template file content
        
        Args:
            module_id (str): ID of the module
            template (Dict[str, Any]): Template configuration
            config (Dict[str, Any]): Module configuration
            
        Returns:
            str: Template content
        """
        description = template.get("description", "")
        
        content = f'''/**
 * {self._to_title_case(module_id)} JavaScript
 * {description}
 * 
 * Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
 */

// Initialize the module when the DOM is loaded
document.addEventListener('DOMContentLoaded', function() {{
    console.log('{self._to_title_case(module_id)} module initialized');
    
    // Get the content container
    const contentElement = document.getElementById('{self._to_kebab_case(module_id)}-content');
    
    if (contentElement) {{
        loadData();
    }}
}});

/**
 * Load data for the {module_id} module
 */
async function loadData() {{
    try {{
        const response = await fetch('/{self._to_kebab_case(module_id)}/api/data');
        const data = await response.json();
        
        if (data.status === 'success') {{
            updateUI(data.data);
        }} else {{
            showError('Failed to load data: ' + data.message);
        }}
    }} catch (error) {{
        console.error('Error loading data:', error);
        showError('An error occurred while loading data');
    }}
}}

/**
 * Update the UI with the loaded data
 * 
 * @param {{Object}} data - The data to display
 */
function updateUI(data) {{
    const contentElement = document.getElementById('{self._to_kebab_case(module_id)}-content');
    
    if (!contentElement) return;
    
    // Replace the loading placeholder with actual content
    contentElement.innerHTML = `
        <div class="bg-white rounded-xl p-4 border border-gray-200">
            <h3 class="text-lg font-semibold mb-2">Your Data</h3>
            <div class="space-y-2">
                <p>Sample data would be displayed here.</p>
            </div>
        </div>
    `;
}}

/**
 * Show an error message
 * 
 * @param {{string}} message - The error message to display
 */
function showError(message) {{
    const contentElement = document.getElementById('{self._to_kebab_case(module_id)}-content');
    
    if (!contentElement) return;
    
    contentElement.innerHTML = `
        <div class="bg-red-50 text-red-800 rounded-xl p-4 border border-red-200">
            <h3 class="text-lg font-semibold mb-2">Error</h3>
            <p>${{message}}</p>
        </div>
    `;
}}
'''
        
        return content
    
    def _generate_model_template(
        self, 
        model_name: str, 
        model: Dict[str, Any], 
        config: Dict[str, Any]
    ) -> str:
        """
        Generate a model template file content
        
        Args:
            model_name (str): Name of the model
            model (Dict[str, Any]): Model configuration
            config (Dict[str, Any]): Module configuration
            
        Returns:
            str: Template content
        """
        attributes = model.get("attributes", [])
        module_id = list(config.keys())[0] if isinstance(config, dict) else ""
        
        content = f'''"""
{model_name} model for {module_id} module

Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from core.database.base import Base


class {model_name}(Base):
    """
    {model_name} model
    """
    __tablename__ = "{self._to_snake_case(model_name)}"
    
    id = Column(String, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
'''
        
        # Add attributes
        for attr in attributes:
            parts = attr.split(":")
            if len(parts) >= 2:
                attr_name = parts[0].strip()
                attr_type = ":".join(parts[1:]).strip()
                
                col_type = self._get_column_type(attr_type)
                content += f"    {attr_name} = {col_type}\n"
        
        content += f'''
    def __repr__(self):
        return f"<{model_name}(id={{self.id}})>"
    
    def to_dict(self):
        """
        Convert the model to a dictionary
        
        Returns:
            Dict[str, Any]: Dictionary representation of the model
        """
        return {{
            "id": self.id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            # Add other attributes here
        }}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "{model_name}":
        """
        Create a model instance from a dictionary
        
        Args:
            data (Dict[str, Any]): Dictionary with model data
            
        Returns:
            {model_name}: Model instance
        """
        return cls(**data)
'''
        
        return content
    
    def _get_column_type(self, attr_type: str) -> str:
        """
        Get the SQLAlchemy column type for an attribute type
        
        Args:
            attr_type (str): Attribute type
            
        Returns:
            str: SQLAlchemy column type
        """
        # Extract comments in parentheses
        comment = ""
        if "(" in attr_type and ")" in attr_type:
            comment_start = attr_type.find("(")
            comment_end = attr_type.rfind(")")
            comment = attr_type[comment_start:comment_end+1]
            attr_type = attr_type[:comment_start].strip() + attr_type[comment_end+1:].strip()
        
        # Basic types
        if attr_type.startswith("str"):
            return f"Column(String){comment}"
        elif attr_type.startswith("int"):
            return f"Column(Integer){comment}"
        elif attr_type.startswith("float"):
            return f"Column(Float){comment}"
        elif attr_type.startswith("bool"):
            return f"Column(Boolean){comment}"
        elif attr_type.startswith("datetime"):
            return f"Column(DateTime){comment}"
        elif attr_type.startswith("Dict") or attr_type.startswith("List") or attr_type.startswith("Any"):
            return f"Column(JSON){comment}"
        elif attr_type.startswith("Optional"):
            # Extract the inner type from Optional[...]
            inner_type = attr_type[attr_type.find("[")+1:attr_type.rfind("]")]
            inner_column = self._get_column_type(inner_type)
            # Modify the column to add nullable=True
            if "Column" in inner_column:
                inner_column = inner_column.replace(")", ", nullable=True)", 1)
            return f"{inner_column}{comment}"
        
        # Default to String
        return f"Column(String){comment}"
    
    @staticmethod
    def _to_snake_case(name: str) -> str:
        """Convert a name to snake_case"""
        import re
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    
    @staticmethod
    def _to_kebab_case(name: str) -> str:
        """Convert a name to kebab-case"""
        return ModuleCreator._to_snake_case(name).replace('_', '-')
    
    @staticmethod
    def _to_class_name(name: str) -> str:
        """Convert a name to CamelCase class name"""
        import re
        parts = re.findall(r'[A-Za-z0-9]+', name)
        return ''.join(p.capitalize() for p in parts)
    
    @staticmethod
    def _to_title_case(name: str) -> str:
        """Convert a name to Title Case"""
        import re
        parts = re.findall(r'[A-Za-z0-9]+', name)
        return ' '.join(p.capitalize() for p in parts)


def main():
    """Main function for the module creator CLI"""
    parser = argparse.ArgumentParser(description='Create modules based on configurations')
    
    # Commands
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # List module configurations
    list_parser = subparsers.add_parser("list", help="List available module configurations")
    
    # Create a module
    create_parser = subparsers.add_parser("create", help="Create a module")
    create_parser.add_argument("module_id", help="ID of the module configuration")
    create_parser.add_argument("--overwrite", action="store_true", help="Overwrite existing files")
    
    # General arguments
    parser.add_argument("--config", "-c", help="Path to the module configuration file", default=CONFIG_PATH)
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Configure logging
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    try:
        creator = ModuleCreator(args.config)
        
        if args.command == "list":
            # List module configurations
            modules = creator.list_modules()
            
            print("\nAvailable Module Configurations:")
            for module in modules:
                print(f"- {module['id']}: {module['description']} (Type: {module['type']})")
        
        elif args.command == "create":
            # Create a module
            options = {"overwrite": args.overwrite}
            target_path = creator.create_module(args.module_id, options)
            
            print(f"\nModule '{args.module_id}' created successfully in {target_path}")
        
        else:
            # Show help if no command is specified
            parser.print_help()
    
    except Exception as e:
        logger.error(f"Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
