# Dynamo MCP

A dynamic MCP registry for cookiecutter templates.

## Overview

Dynamo MCP is a system that exposes cookiecutter templates through the Model Context Protocol (MCP). It allows you to discover, register, and manage cookiecutter templates, and generate projects from them.

## Features

- **Template Registry**: Discover, add, update, and remove cookiecutter templates
- **Environment Manager**: Create and manage virtual environments for templates
- **Interface Generator**: Extract variables from templates
- **Project Generator**: Generate projects from templates
- **MCP Server**: Expose template functionality through the Model Context Protocol
- **SSE Transport Layer**: Communicate with the MCP server over Server-Sent Events
- **API Gateway**: Expose the MCP server through a REST API

## Installation

```bash
# Clone the repository
git clone https://github.com/example/dynamo-mcp.git
cd dynamo-mcp

# Install the package
pip install -e .
```

## Usage

### Starting the MCP Server

```bash
# Start the MCP server with SSE transport (default)
dynamo-mcp

# Start the MCP server with stdio transport
dynamo-mcp --transport stdio

# Start the MCP server with custom host and port
dynamo-mcp --host 0.0.0.0 --port 8000
```

### Using the MCP Server

The MCP server exposes the following tools:

- `list_templates`: List all available cookiecutter templates
- `add_template`: Add a new cookiecutter template
- `update_template`: Update a cookiecutter template
- `remove_template`: Remove a cookiecutter template
- `discover_templates`: Discover popular cookiecutter templates
- `get_template_variables`: Get the variables for a cookiecutter template
- `create_project`: Create a project from a cookiecutter template

The MCP server also exposes the following resources:

- `templates://list`: List all available cookiecutter templates
- `templates://{name}/variables`: Get the variables for a specific cookiecutter template
- `templates://{name}/info`: Get information about a specific cookiecutter template

### Example: Adding a Template

```python
import asyncio
from fastmcp import FastMCPClient

async def main():
    # Connect to the MCP server
    client = FastMCPClient("http://localhost:3000")
    
    # Add a template
    template = await client.call_tool("add_template", {
        "url": "https://github.com/audreyfeldroy/cookiecutter-pypackage.git",
        "name": "python-package",
        "description": "A cookiecutter template for creating Python packages"
    })
    
    print(f"Added template: {template}")

asyncio.run(main())
```

### Example: Creating a Project

```python
import asyncio
from fastmcp import FastMCPClient

async def main():
    # Connect to the MCP server
    client = FastMCPClient("http://localhost:3000")
    
    # Create a project
    project_path = await client.call_tool("create_project", {
        "template_name": "python-package",
        "output_dir": "projects",
        "variables": {
            "project_name": "My Project",
            "project_slug": "my_project",
            "project_short_description": "A sample project",
            "full_name": "John Doe",
            "email": "john@example.com",
            "github_username": "johndoe",
            "version": "0.1.0",
            "command_line_interface": "Click",
            "use_pytest": "y",
            "use_black": "y",
            "use_pypi_deployment_with_travis": "y",
            "add_pyup_badge": "y",
            "create_author_file": "y",
            "open_source_license": "MIT"
        }
    })
    
    print(f"Created project at: {project_path}")

asyncio.run(main())
```

## Configuration

The following environment variables can be used to configure the system:

- `DYNAMO_MCP_BASE_DIR`: Base directory for templates and virtual environments (default: `~/.dynamo-mcp`)
- `DYNAMO_MCP_TEMPLATES_DIR`: Directory for templates (default: `~/.dynamo-mcp/templates`)
- `DYNAMO_MCP_VENVS_DIR`: Directory for virtual environments (default: `~/.dynamo-mcp/venvs`)
- `DYNAMO_MCP_HOST`: Host to bind to (default: `localhost`)
- `DYNAMO_MCP_PORT`: Port to bind to (default: `3000`)
- `DYNAMO_MCP_TRANSPORT`: Transport type (default: `sse`)
- `DYNAMO_MCP_AUTH_ENABLED`: Enable authentication (default: `false`)
- `DYNAMO_MCP_AUTH_USERNAME`: Authentication username (default: `admin`)
- `DYNAMO_MCP_AUTH_PASSWORD`: Authentication password (default: `password`)

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run a specific test
pytest tests/test_basic.py

# Run a comprehensive test
python tests/comprehensive_test.py
```

### Project Structure

- `dynamo_mcp/`: Main package
  - `api/`: API components
    - `mcp_server.py`: MCP server
    - `sse_transport.py`: SSE transport layer
  - `core/`: Core components
    - `environment_manager.py`: Environment manager
    - `interface_generator.py`: Interface generator
    - `models.py`: Data models
    - `project_generator.py`: Project generator
    - `template_registry.py`: Template registry
  - `utils/`: Utility components
    - `config.py`: Configuration
    - `exceptions.py`: Exceptions
  - `main.py`: Main entry point
- `tests/`: Tests
  - `test_basic.py`: Basic tests
  - `test_mcp_stdio.py`: MCP stdio transport tests
  - `comprehensive_test.py`: Comprehensive tests

## License

This project is licensed under the MIT License - see the LICENSE file for details.
