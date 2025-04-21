# Contributing to MCP-Powered Deployment Automation

Thank you for your interest in contributing to the MCP-Powered Deployment Automation project! This document provides guidelines and instructions for contributing to this repository.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Branching Strategy](#branching-strategy)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Adding New Platforms](#adding-new-platforms)
- [Documentation](#documentation)
- [Testing](#testing)

## Code of Conduct

This project adheres to a code of conduct that expects all contributors to be respectful, inclusive, and considerate. By participating, you are expected to uphold this code.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally
3. Set up the development environment (see below)
4. Create a new branch for your feature or bugfix
5. Make your changes
6. Push your branch to your fork
7. Submit a pull request to the main repository

## Development Setup

### Prerequisites

- Python 3.6 or higher
- PowerShell 5.1 or higher (for Windows users)
- Git
- Node.js and npm (for MCP servers)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/deployment-automation.git
cd deployment-automation

# Install dependencies
pip install -r requirements.txt
pip install -e .  # Install in development mode

# Install MCP servers
npm install -g hyperbrowser-mcp @modelcontextprotocol/fetch-mcp
```

## Branching Strategy

We follow a simplified Git workflow:

- `main` - The primary branch containing the latest production-ready code
- `feature/<feature-name>` - For new features
- `bugfix/<bug-description>` - For bug fixes
- `docs/<documentation-update>` - For documentation updates
- `platform/<platform-name>` - For adding support for new platforms

## Pull Request Process

1. Ensure your code follows the project's coding standards
2. Update the documentation if necessary
3. Make sure all tests pass
4. Submit the pull request with a clear description of the changes
5. Wait for a review from a project maintainer
6. Address any feedback that is provided
7. Once approved, a maintainer will merge your pull request

## Coding Standards

- Python code should follow PEP 8 guidelines
- PowerShell code should follow the [PowerShell Best Practices and Style Guide](https://github.com/PoshCode/PowerShellPracticeAndStyle)
- Use descriptive variable and function names
- Document all functions, classes, and modules with docstrings
- Keep functions focused on a single responsibility
- Include appropriate error handling

## Adding New Platforms

To add support for a new platform:

1. Create a new Python module in the `src/platforms` directory
2. Implement the required interface methods (see existing platforms for reference)
3. Register the platform in `src/platforms/__init__.py`
4. Update configuration in `config.json` to include the new platform
5. Document the platform's usage in README.md
6. Add tests for the new platform

Example platform module structure:

```python
"""
NewPlatform integration
"""

class NewPlatform:
    """New platform handler"""
    
    def __init__(self, token=None):
        self.token = token
        
    def deploy(self):
        """Deploy to the platform"""
        # Implementation goes here
        
    def get_logs(self):
        """Get logs from the platform"""
        # Implementation goes here
```

## Documentation

All new features or changes should be documented:

- Update README.md for user-facing changes
- Update function and class docstrings for implementation details
- For major changes, add or update markdown files in the project root

## Testing

- Write unit tests for all new functionality
- Run existing tests before submitting a pull request
- Update tests when modifying existing functionality

To run tests:

```bash
# Run all tests
pytest

# Run tests for a specific module
pytest tests/test_specific_module.py
```

---

Thank you for contributing to the MCP-Powered Deployment Automation project! Your efforts help make cloud deployment easier and more reliable for everyone.
