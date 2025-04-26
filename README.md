<p align="center">
  <img src="assets/dynamo-mcp.png" alt="Dynamo MCP Logo">
</p>

# Dynamo MCP

Dynamo MCP is a system that exposes cookiecutter templates through the Model Context Protocol (MCP). It allows you to discover, register, and manage cookiecutter templates, and generate projects from them - enabling a more efficient, error-free "Vibe coding" experience.

## What is Cookiecutter?

[Cookiecutter](https://github.com/cookiecutter/cookiecutter) is a command-line tool that generates projects from templates. It uses a template directory with a cookiecutter.json file to create customized project structures.

Templates enable rapid project scaffolding with best practices built-in. The cookiecutter ecosystem offers thousands of community-maintained templates across programming languages and frameworks, encapsulating collective expertise for developers to leverage instantly.

## What is Vibe Coding?

"Vibe coding" is a modern approach where developers use AI tools to generate code from natural language prompts. Developers describe functionality in plain language while AI handles implementation details.

The synergy between cookiecutter templates, MCP, and AI creates a powerful development workflow:
- Templates provide structured foundations with best practices
- MCP enables seamless template discovery and integration
- AI tools customize and extend template-based code

This combination dramatically reduces errors, accelerates development, and lets developers focus on high-level design rather than repetitive coding tasks.

## Why Templates Matter: The Vibe Coding Approach

Great coding starts with great templates. Templates form the foundation of the Vibe Coding approach, combining efficiency, consistency, and enjoyment. When paired with AI-powered code generation, the result is nearly error-free development that maximizes productivity.

### Benefits at a Glance

- **Faster Development**: Skip repetitive boilerplate and focus on unique business logic
- **Efficient Workflows**: Leverage pre-configured best practices and structures
- **Cost-Effective**: Eliminate time spent on setup and architecture decisions
- **Consistent Quality**: Enforce standards across projects and teams
- **Lower Learning Curve**: Help new team members understand projects quickly

Dynamo MCP's extensive template library gives you instant access to templates for virtually any project type, letting you start building with good vibes from day one.

## Features

- **Template Registry**: Discover, add, update, and remove cookiecutter templates
- **Template Database**: Store and manage templates in a SQLite database with categorization, tagging, and search capabilities
- **Default Template Library**: Access a comprehensive library of 50+ pre-defined templates across various categories
- **Environment Manager**: Create and manage virtual environments for templates
- **Interface Generator**: Extract variables from templates
- **Project Generator**: Generate projects from templates
- **MCP Server**: Expose template functionality through the Model Context Protocol
- **SSE Transport Layer**: Communicate with the MCP server over Server-Sent Events
- **API Gateway**: Expose the MCP server through a REST API

## Installation

```bash
# Clone the repository
git clone https://github.com/ruvnet/dynamo-mcp.git
cd dynamo-mcp

# Install the package
pip install -e .
```

## Using as a Cookiecutter Template

You can use this repository as a cookiecutter template to create your own MCP server:

```bash
# Install cookiecutter if you haven't already
pip install cookiecutter

# Create a new project from the template
cookiecutter https://github.com/ruvnet/dynamo-mcp

# Follow the prompts to customize your project
```

This will create a new project with the following features:
- Fully functional MCP server with SQLite database integration
- Customizable project name, author, and license
- Pre-configured virtual environment setup
- Optional pytest and black integration

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
- `list_templates_by_category`: List templates filtered by category
- `get_categories`: Get all unique template categories
- `search_templates`: Search templates by name, description, category, or tags
- `add_template`: Add a new cookiecutter template
- `update_template`: Update a cookiecutter template
- `remove_template`: Remove a cookiecutter template
- `discover_templates`: Discover templates from the default template library
- `get_template_variables`: Get the variables for a cookiecutter template
- `create_project`: Create a project from a cookiecutter template

The MCP server also exposes the following resources:

- `templates://list`: List all available cookiecutter templates
- `templates://categories`: List all template categories
- `templates://category/{category}`: List templates in a specific category
- `templates://search/{query}`: Search templates by query
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

### Example: Searching Templates by Category

```python
import asyncio
from fastmcp import FastMCPClient

async def main():
    # Connect to the MCP server
    client = FastMCPClient("http://localhost:3000")
    
    # Get all categories
    categories = await client.call_tool("get_categories", {})
    print(f"Available categories: {categories}")
    
    # List templates in a specific category
    python_templates = await client.call_tool("list_templates_by_category", {
        "category": "Python"
    })
    
    print(f"Python templates: {python_templates}")

asyncio.run(main())
```

### Example: Searching Templates

```python
import asyncio
from fastmcp import FastMCPClient

async def main():
    # Connect to the MCP server
    client = FastMCPClient("http://localhost:3000")
    
    # Search for templates
    django_templates = await client.call_tool("search_templates", {
        "query": "django"
    })
    
    print(f"Django-related templates: {django_templates}")
    
    # Access search resource directly
    flask_templates = await client.access_resource("templates://search/flask")
    print(f"Flask-related templates: {flask_templates}")

asyncio.run(main())
```

## Template Database

The system includes a SQLite database for storing and managing templates. The database provides the following features:

- **Categorization**: Templates are organized into categories for easy discovery
- **Tagging**: Templates can be tagged for additional organization
- **Search**: Templates can be searched by name, description, category, or tags
- **Default Library**: The database is pre-populated with 50+ popular templates across various categories

### Database Schema

The database schema is defined in `dynamo_mcp/sql/schema.sql` and includes the following tables:

- **templates**: Stores template information
  - `id`: Unique identifier
  - `name`: Template name
  - `url`: Template repository URL
  - `description`: Template description
  - `category`: Template category
  - `tags`: Comma-separated list of tags
  - `created_at`: Creation timestamp

- **template_versions**: Stores version information for templates
  - `id`: Unique identifier
  - `template_id`: Reference to templates.id
  - `version`: Version string
  - `git_hash`: Git hash of the version
  - `created_at`: Creation timestamp

- **template_dependencies**: Stores dependencies between templates
  - `id`: Unique identifier
  - `template_id`: Reference to templates.id
  - `dependency_id`: Reference to templates.id
  - `optional`: Whether the dependency is optional

### Database Initialization

The database is automatically initialized when the system starts. You can also manually initialize or reset the database:

```bash
# Initialize the database with default templates
python -m dynamo_mcp.scripts.init_db

# Reset the database (delete and recreate)
python -m dynamo_mcp.scripts.init_db --reset

# Initialize the database using the SQL schema file
python -m dynamo_mcp.scripts.init_db_from_sql

# Initialize only the schema without adding templates
python -m dynamo_mcp.scripts.init_db_from_sql --schema-only
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
    - `database.py`: Database utilities
    - `exceptions.py`: Exceptions
    - `init_template_db.py`: Database initialization
  - `scripts/`: Scripts
    - `init_db.py`: Database initialization script
    - `init_db_from_sql.py`: Database initialization from SQL schema
  - `sql/`: SQL files
    - `schema.sql`: Database schema definition
  - `main.py`: Main entry point
- `tests/`: Tests
  - `test_basic.py`: Basic tests
  - `test_database.py`: Database tests
  - `test_mcp_stdio.py`: MCP stdio transport tests
  - `comprehensive_test.py`: Comprehensive tests

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Converting to a Full Cookiecutter Template

This repository is already set up with the basic cookiecutter template structure (cookiecutter.json and hooks). To convert it to a full cookiecutter template with proper variable substitution:

```bash
# Run the conversion script
python scripts/convert_to_template.py

# Test the template locally
cookiecutter .

# If everything looks good, commit and push to GitHub
git add .
git commit -m "Convert to cookiecutter template"
git push
```

After pushing to GitHub, users can create new projects from your template using:

```bash
cookiecutter https://github.com/ruvnet/dynamo-mcp
```
