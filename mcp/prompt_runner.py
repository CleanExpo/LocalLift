#!/usr/bin/env python
"""
Prompt Runner for LocalLift

This script loads prompts from the prompt library and executes them against
language models. It can be used to generate code, documentation, tests,
and other artifacts based on templates.
"""
import os
import sys
import json
import argparse
import re
import time
from typing import Dict, Any, List, Optional, Union, Callable
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("prompt_runner")

# Default paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_LIBRARY_PATH = os.path.join(SCRIPT_DIR, "prompt_library.json")
DEFAULT_OUTPUT_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "generated")


class PromptLibrary:
    """Manages the prompt library and provides methods to access prompts"""
    
    def __init__(self, library_path: str = DEFAULT_LIBRARY_PATH):
        """
        Initialize the prompt library
        
        Args:
            library_path (str): Path to the prompt library JSON file
        """
        self.library_path = library_path
        self.prompts = {}
        self.categories = {}
        self.metadata = {}
        self._load_library()
    
    def _load_library(self):
        """Load the prompt library from the JSON file"""
        try:
            with open(self.library_path, 'r') as f:
                data = json.load(f)
                
            self.prompts = data.get("prompts", {})
            self.categories = data.get("categories", {})
            self.metadata = data.get("metadata", {})
                
            logger.info(f"Loaded prompt library version {self.metadata.get('version', 'unknown')}")
            logger.info(f"Found {len(self.prompts)} prompts in {len(self.categories)} categories")
        except Exception as e:
            logger.error(f"Failed to load prompt library: {e}")
            raise
    
    def get_prompt(self, prompt_id: str) -> Dict[str, Any]:
        """
        Get a prompt by ID
        
        Args:
            prompt_id (str): ID of the prompt to get
            
        Returns:
            Dict[str, Any]: Prompt data
            
        Raises:
            ValueError: If the prompt ID is not found
        """
        if prompt_id not in self.prompts:
            raise ValueError(f"Prompt ID '{prompt_id}' not found in library")
        
        return self.prompts[prompt_id]
    
    def list_prompts(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List available prompts
        
        Args:
            category (str, optional): Category to filter by
            
        Returns:
            List[Dict[str, Any]]: List of prompts
        """
        if category and category in self.categories:
            prompt_ids = self.categories[category]
            prompts = [
                {"id": pid, **self.prompts[pid]} 
                for pid in prompt_ids 
                if pid in self.prompts
            ]
        else:
            prompts = [
                {"id": pid, **prompt} 
                for pid, prompt in self.prompts.items()
            ]
            
        return prompts
    
    def list_categories(self) -> List[str]:
        """
        List available categories
        
        Returns:
            List[str]: List of category names
        """
        return list(self.categories.keys())


class PromptFormatter:
    """Formats prompts by replacing parameters with values"""
    
    @staticmethod
    def format_prompt(prompt_template: str, parameters: Dict[str, Any]) -> str:
        """
        Format a prompt template by replacing parameters
        
        Args:
            prompt_template (str): Prompt template with {{parameter}} placeholders
            parameters (Dict[str, Any]): Parameter values
            
        Returns:
            str: Formatted prompt
        """
        formatted = prompt_template
        
        # Replace each parameter in the template
        for param_name, param_value in parameters.items():
            placeholder = f"{{{{{param_name}}}}}"
            formatted = formatted.replace(placeholder, str(param_value))
            
        return formatted
    
    @staticmethod
    def validate_parameters(prompt: Dict[str, Any], parameters: Dict[str, Any]) -> List[str]:
        """
        Validate that all required parameters are provided
        
        Args:
            prompt (Dict[str, Any]): Prompt data
            parameters (Dict[str, Any]): Parameter values
            
        Returns:
            List[str]: List of missing parameter names
        """
        missing = []
        prompt_params = prompt.get("parameters", {})
        
        for param_name, param_info in prompt_params.items():
            is_required = param_info.get("required", False)
            if is_required and param_name not in parameters:
                missing.append(param_name)
                
        return missing


class LLMProvider:
    """Base class for language model providers"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the LLM provider
        
        Args:
            api_key (str, optional): API key for the provider
        """
        self.api_key = api_key or os.environ.get(self._get_api_key_env_var())
        
    def _get_api_key_env_var(self) -> str:
        """
        Get the environment variable name for the API key
        
        Returns:
            str: Environment variable name
        """
        raise NotImplementedError("Subclasses must implement this method")
    
    def generate_completion(self, prompt: str, options: Dict[str, Any] = None) -> str:
        """
        Generate a completion for a prompt
        
        Args:
            prompt (str): Prompt to generate a completion for
            options (Dict[str, Any], optional): Additional options for the completion
            
        Returns:
            str: Generated completion
        """
        raise NotImplementedError("Subclasses must implement this method")


class OpenAIProvider(LLMProvider):
    """OpenAI language model provider"""
    
    def _get_api_key_env_var(self) -> str:
        return "OPENAI_API_KEY"
    
    def generate_completion(self, prompt: str, options: Dict[str, Any] = None) -> str:
        """
        Generate a completion using the OpenAI API
        
        Args:
            prompt (str): Prompt to generate a completion for
            options (Dict[str, Any], optional): Additional options for the completion
            
        Returns:
            str: Generated completion
        """
        try:
            import openai
            
            if not self.api_key:
                raise ValueError("OpenAI API key is required")
            
            openai.api_key = self.api_key
            opts = options or {}
            
            model = opts.get("model", "gpt-4-0314")
            max_tokens = opts.get("max_tokens", 2000)
            temperature = opts.get("temperature", 0.7)
            
            logger.info(f"Generating completion with OpenAI model {model}")
            
            response = openai.ChatCompletion.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant that generates high-quality code and documentation for the LocalLift platform."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            return response.choices[0].message.content
        except ImportError:
            logger.error("OpenAI package not installed. Run 'pip install openai'")
            raise
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise


class AnthropicProvider(LLMProvider):
    """Anthropic language model provider"""
    
    def _get_api_key_env_var(self) -> str:
        return "ANTHROPIC_API_KEY"
    
    def generate_completion(self, prompt: str, options: Dict[str, Any] = None) -> str:
        """
        Generate a completion using the Anthropic API
        
        Args:
            prompt (str): Prompt to generate a completion for
            options (Dict[str, Any], optional): Additional options for the completion
            
        Returns:
            str: Generated completion
        """
        try:
            from anthropic import Anthropic
            
            if not self.api_key:
                raise ValueError("Anthropic API key is required")
            
            anthropic = Anthropic(api_key=self.api_key)
            opts = options or {}
            
            model = opts.get("model", "claude-2")
            max_tokens = opts.get("max_tokens", 2000)
            temperature = opts.get("temperature", 0.7)
            
            logger.info(f"Generating completion with Anthropic model {model}")
            
            response = anthropic.completions.create(
                model=model,
                prompt=f"\n\nHuman: {prompt}\n\nAssistant:",
                max_tokens_to_sample=max_tokens,
                temperature=temperature
            )
            
            return response.completion
        except ImportError:
            logger.error("Anthropic package not installed. Run 'pip install anthropic'")
            raise
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise


class PromptRunner:
    """
    Runs prompts using a language model provider
    """
    
    def __init__(
        self, 
        library_path: str = DEFAULT_LIBRARY_PATH,
        output_dir: str = DEFAULT_OUTPUT_DIR,
        provider: str = "openai",
        api_key: Optional[str] = None
    ):
        """
        Initialize the prompt runner
        
        Args:
            library_path (str): Path to the prompt library
            output_dir (str): Directory to save output
            provider (str): Language model provider
            api_key (str, optional): API key for the provider
        """
        self.library = PromptLibrary(library_path)
        self.output_dir = output_dir
        self.provider = self._get_provider(provider, api_key)
        
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    def _get_provider(self, provider: str, api_key: Optional[str] = None) -> LLMProvider:
        """
        Get a language model provider
        
        Args:
            provider (str): Provider name
            api_key (str, optional): API key for the provider
            
        Returns:
            LLMProvider: Language model provider
            
        Raises:
            ValueError: If the provider is not supported
        """
        if provider.lower() == "openai":
            return OpenAIProvider(api_key)
        elif provider.lower() == "anthropic":
            return AnthropicProvider(api_key)
        else:
            raise ValueError(f"Provider '{provider}' not supported")
    
    def run_prompt(
        self, 
        prompt_id: str, 
        parameters: Dict[str, Any],
        output_file: Optional[str] = None,
        options: Dict[str, Any] = None
    ) -> str:
        """
        Run a prompt and get the generated result
        
        Args:
            prompt_id (str): ID of the prompt to run
            parameters (Dict[str, Any]): Parameter values
            output_file (str, optional): File to save the output to
            options (Dict[str, Any], optional): Additional options for the LLM
            
        Returns:
            str: Generated result
        """
        # Get the prompt template
        prompt_data = self.library.get_prompt(prompt_id)
        prompt_template = prompt_data["prompt"]
        
        # Validate parameters
        missing = PromptFormatter.validate_parameters(prompt_data, parameters)
        if missing:
            raise ValueError(f"Missing required parameters: {', '.join(missing)}")
        
        # Format the prompt
        formatted_prompt = PromptFormatter.format_prompt(prompt_template, parameters)
        
        # Generate the result
        result = self.provider.generate_completion(formatted_prompt, options)
        
        # Save the result if an output file is specified
        if output_file:
            output_path = os.path.join(self.output_dir, output_file)
            with open(output_path, 'w') as f:
                f.write(result)
            logger.info(f"Result saved to {output_path}")
        
        return result


def main():
    """Main function for the prompt runner CLI"""
    parser = argparse.ArgumentParser(description='Run prompts from the prompt library')
    
    # Commands
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # List prompts
    list_parser = subparsers.add_parser("list", help="List available prompts")
    list_parser.add_argument("--category", "-c", help="Category to filter by")
    
    # Run a prompt
    run_parser = subparsers.add_parser("run", help="Run a prompt")
    run_parser.add_argument("prompt_id", help="ID of the prompt to run")
    run_parser.add_argument("--params", "-p", help="Parameters in JSON format")
    run_parser.add_argument("--output", "-o", help="File to save the output to")
    run_parser.add_argument("--provider", help="Language model provider", default="openai")
    run_parser.add_argument("--options", help="Additional options for the LLM in JSON format")
    
    # General arguments
    parser.add_argument("--library", "-l", help="Path to the prompt library", default=DEFAULT_LIBRARY_PATH)
    parser.add_argument("--output-dir", "-d", help="Directory to save output", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Configure logging
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    try:
        if args.command == "list":
            # List prompts
            library = PromptLibrary(args.library)
            prompts = library.list_prompts(args.category)
            
            print("\nAvailable Prompts:")
            for prompt in prompts:
                print(f"- {prompt['id']}: {prompt['name']} - {prompt['description']}")
            
            if not args.category:
                print("\nCategories:")
                for category in library.list_categories():
                    print(f"- {category}")
        
        elif args.command == "run":
            # Parse parameters
            params = json.loads(args.params) if args.params else {}
            
            # Parse options
            options = json.loads(args.options) if args.options else {}
            
            # Run the prompt
            runner = PromptRunner(
                library_path=args.library,
                output_dir=args.output_dir,
                provider=args.provider
            )
            
            result = runner.run_prompt(
                args.prompt_id,
                params,
                args.output,
                options
            )
            
            # Print the result if no output file is specified
            if not args.output:
                print("\n" + "=" * 80)
                print("Generated Result:")
                print("=" * 80 + "\n")
                print(result)
                print("\n" + "=" * 80)
        
        else:
            # Show help if no command is specified
            parser.print_help()
    
    except Exception as e:
        logger.error(f"Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
