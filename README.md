# dynamo-mcp
A dyamic MCP Registry using Cookiecutter templates
# FastMCP Cookiecutter Template Interface Generator

This implementation creates a dynamic MCP (Model Context Protocol) server that manages isolated virtual environments for different cookiecutter templates, allowing you to generate projects through an SSE interface. The system automatically discovers, loads, and exposes cookiecutter templates as MCP tools and resources.

## Architecture Overview

The system consists of a primary FastMCP server that manages multiple virtual environments, each containing a specific cookiecutter template. All templates are exposed through a unified SSE endpoint for easy integration with LLM-powered applications like Claude.

### Key Components

- **Template Management**: Discover, add, update, and remove cookiecutter templates
- **Virtual Environment Isolation**: Each template runs in its own virtual environment
- **Dynamic Interface Generation**: Automatically create MCP interfaces from cookiecutter configuration
- **SSE Transport**: Expose all functionality through Server-Sent Events for web compatibility

## Implementation

### Core Server Implementation

```python
# cookiecutter_mcp.py
import os
import json
import asyncio
import subprocess
import venv
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from fastmcp import FastMCP, Context
from pydantic import BaseModel, Field

class TemplateInfo(BaseModel):
    """Information about a cookiecutter template."""
    name: str
    description: str
    url: str
    venv_path: Optional[str] = None
    is_active: bool = False
    last_updated: Optional[str] = None
    variables_cache: Optional[List[Dict[str, Any]]] = Field(default=None, exclude=True)

class TemplateVariable(BaseModel):
    """A variable for a cookiecutter template."""
    name: str
    description: str
    default: Optional[str] = None
    choices: Optional[List[str]] = None
    required: bool = True
    type: str = "string"

class CreateProjectRequest(BaseModel):
    """Request to create a project from a template."""
    template_name: str
    output_dir: str
    variables: Dict[str, Any]

# Main FastMCP server
mcp = FastMCP("Cookiecutter Templates", dependencies=["cookiecutter"])

# Directory structure
VENVS_DIR = Path("./venvs")
TEMPLATES_DIR = Path("./templates")
OUTPUTS_DIR = Path("./outputs")

# Ensure directories exist
VENVS_DIR.mkdir(exist_ok=True)
TEMPLATES_DIR.mkdir(exist_ok=True)
OUTPUTS_DIR.mkdir(exist_ok=True)

# Store information about available templates
templates: Dict[str, TemplateInfo] = {}
```

### Helper Functions

```python
async def _run_in_venv(venv_path: Path, cmd: List[str], ctx: Optional[Context] = None) -> str:
    """Run a command in a virtual environment."""
    if os.name == "nt":  # Windows
        python_path = venv_path / "Scripts" / "python"
    else:  # Unix-like
        python_path = venv_path / "bin" / "python"
    
    cmd_str = " ".join([str(python_path), "-m"] + cmd)
    if ctx:
        await ctx.info(f"Running: {cmd_str}")
    
    process = await asyncio.create_subprocess_exec(
        str(python_path), "-m", *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    stdout, stderr = await process.communicate()
    
    if process.returncode != 0:
        error_msg = stderr.decode()
        if ctx:
            await ctx.error(f"Command failed: {error_msg}")
        raise RuntimeError(f"Command failed: {error_msg}")
    
    return stdout.decode().strip()

async def _get_template_variables(template_dir: Path) -> List[TemplateVariable]:
    """Extract variables from a cookiecutter.json file."""
    cookiecutter_file = template_dir / "cookiecutter.json"
    if not cookiecutter_file.exists():
        raise FileNotFoundError(f"cookiecutter.json not found in {template_dir}")
    
    with open(cookiecutter_file) as f:
        cookiecutter_json = json.load(f)
    
    variables = []
    for key, value in cookiecutter_json.items():
        if key.startswith("_"):
            continue  # Skip internal variables
        
        description = f"Variable {key}"
        
        variable = TemplateVariable(name=key, description=description)
        
        if isinstance(value, str):
            variable.default = value
            variable.type = "string"
        elif isinstance(value, bool):
            variable.default = str(value).lower()
            variable.type = "boolean"
        elif isinstance(value, (int, float)):
            variable.default = str(value)
            variable.type = "number"
        elif isinstance(value, list):
            variable.choices = [str(v) for v in value]
            if value:
                variable.default = str(value[0])
            variable.type = "choice"
        
        variables.append(variable)
    
    return variables
```

### MCP Tools

```python
@mcp.tool()
async def list_templates() -> List[TemplateInfo]:
    """List all available cookiecutter templates."""
    return list(templates.values())

@mcp.tool()
async def get_template_variables(template_name: str, ctx: Context) -> List[TemplateVariable]:
    """Get the variables for a cookiecutter template."""
    if template_name not in templates:
        await ctx.error(f"Template {template_name} not found")
        raise ValueError(f"Template {template_name} not found")
    
    template = templates[template_name]
    if not template.venv_path:
        await ctx.error(f"Template {template_name} environment not initialized")
        raise ValueError(f"Template {template_name} environment not initialized")
    
    # Check if we have cached variables
    if template.variables_cache:
        return [TemplateVariable(**v) for v in template.variables_cache]
    
    try:
        # Load the cookiecutter.json file to get variables
        template_dir = Path(template.venv_path) / "template"
        variables = await _get_template_variables(template_dir)
        
        # Cache the variables
        template.variables_cache = [v.dict() for v in variables]
        with open(TEMPLATES_DIR / f"{template_name}.json", "w") as f:
            f.write(template.json(exclude={"variables_cache"}))
        
        return variables
    except Exception as e:
        await ctx.error(f"Failed to get template variables: {str(e)}")
        raise

@mcp.tool()
async def add_template(url: str, ctx: Context, name: Optional[str] = None, 
                      description: Optional[str] = None) -> TemplateInfo:
    """Add a new cookiecutter template and create a virtual environment for it."""
    # Extract name from URL if not provided
    if not name:
        name = url.split("/")[-1].replace("cookiecutter-", "")
        if not name:
            name = url.split("/")[-2]
    
    await ctx.info(f"Adding template {name} from {url}")
    
    # Create template info
    template = TemplateInfo(
        name=name,
        description=description or f"Cookiecutter template from {url}",
        url=url,
        is_active=False,
        last_updated=datetime.now().isoformat()
    )
    
    # Create virtual environment for this template
    venv_path = VENVS_DIR / name
    if venv_path.exists():
        await ctx.warning(f"Virtual environment for {name} already exists, removing it")
        shutil.rmtree(venv_path)
    
    template.venv_path = str(venv_path)
    
    try:
        # Create venv
        await ctx.info(f"Creating virtual environment for {name}")
        venv.create(venv_path, with_pip=True)
        
        # Install cookiecutter in the venv
        if os.name == "nt":  # Windows
            pip_path = venv_path / "Scripts" / "pip"
        else:  # Unix-like
            pip_path = venv_path / "bin" / "pip"
        
        await ctx.info(f"Installing cookiecutter in {name} environment")
        subprocess.run([str(pip_path), "install", "cookiecutter"], check=True)
        
        # Clone the template repository
        template_dir = venv_path / "template"
        template_dir.mkdir(exist_ok=True)
        
        await ctx.info(f"Cloning template {url}")
        await _run_in_venv(venv_path, ["cookiecutter", "--no-input", url, 
                                     "--output-dir", str(template_dir)], ctx)
        
        # Try to get variables to cache them
        try:
            variables = await _get_template_variables(template_dir)
            template.variables_cache = [v.dict() for v in variables]
            await ctx.info(f"Cached {len(variables)} variables for {name}")
        except Exception as e:
            await ctx.warning(f"Failed to cache template variables: {str(e)}")
        
        # Save template info
        templates[name] = template
        with open(TEMPLATES_DIR / f"{name}.json", "w") as f:
            f.write(template.json(exclude={"variables_cache"}))
        
        await ctx.info(f"Template {name} added successfully")
        return template
    except Exception as e:
        await ctx.error(f"Failed to add template: {str(e)}")
        # Clean up
        if venv_path.exists():
            shutil.rmtree(venv_path)
        raise

@mcp.tool()
async def create_project(request: CreateProjectRequest, ctx: Context) -> str:
    """Create a project from a cookiecutter template."""
    if request.template_name not in templates:
        await ctx.error(f"Template {request.template_name} not found")
        raise ValueError(f"Template {request.template_name} not found")
    
    template = templates[request.template_name]
    if not template.venv_path:
        await ctx.error(f"Template {request.template_name} environment not initialized")
        raise ValueError(f"Template {request.template_name} environment not initialized")
    
    venv_path = Path(template.venv_path)
    output_dir = Path(request.output_dir)
    if not output_dir.is_absolute():
        output_dir = OUTPUTS_DIR / output_dir
    
    output_dir.mkdir(exist_ok=True, parents=True)
    
    # Prepare variables for cookiecutter
    config_file = output_dir / "cookiecutter.json"
    with open(config_file, "w") as f:
        json.dump(request.variables, f)
    
    await ctx.info(f"Creating project from template {request.template_name} in {output_dir}")
    
    try:
        # Run cookiecutter with the provided variables
        output = await _run_in_venv(
            venv_path,
            ["cookiecutter", template.url, "--output-dir", str(output_dir), 
             "--no-input", "--config-file", str(config_file)],
            ctx
        )
        
        # Clean up
        config_file.unlink()
        
        await ctx.info(f"Project created successfully in {output_dir}")
        return f"Project created successfully in {output_dir}\n{output}"
    except Exception as e:
        await ctx.error(f"Failed to create project: {str(e)}")
        if config_file.exists():
            config_file.unlink()
        raise
```

### Additional Tools

```python
@mcp.tool()
async def update_template(template_name: str, ctx: Context, force: bool = False) -> TemplateInfo:
    """Update a cookiecutter template to the latest version."""
    if template_name not in templates:
        await ctx.error(f"Template {template_name} not found")
        raise ValueError(f"Template {template_name} not found")
    
    template = templates[template_name]
    
    if not force:
        await ctx.info(f"Checking if template {template_name} needs updating")
        # Here you could implement logic to check if the template actually needs updating
    
    # Re-add the template to update it
    return await add_template(template.url, ctx, template.name, template.description)

@mcp.tool()
async def remove_template(template_name: str, ctx: Context) -> str:
    """Remove a cookiecutter template and its virtual environment."""
    if template_name not in templates:
        await ctx.error(f"Template {template_name} not found")
        raise ValueError(f"Template {template_name} not found")
    
    template = templates[template_name]
    venv_path = Path(template.venv_path) if template.venv_path else None
    
    # Remove the template's virtual environment
    if venv_path and venv_path.exists():
        await ctx.info(f"Removing virtual environment for {template_name}")
        shutil.rmtree(venv_path)
    
    # Remove the template's info file
    template_file = TEMPLATES_DIR / f"{template_name}.json"
    if template_file.exists():
        template_file.unlink()
    
    # Remove from in-memory storage
    del templates[template_name]
    
    await ctx.info(f"Template {template_name} removed successfully")
    return f"Template {template_name} removed successfully"

@mcp.tool()
async def discover_templates(ctx: Context) -> List[TemplateInfo]:
    """Discover popular cookiecutter templates from GitHub."""
    await ctx.info("Discovering popular cookiecutter templates from GitHub")
    
    # Popular templates (could be expanded to use GitHub API)
    popular_templates = [
        {"name": "python-package", "url": "https://github.com/audreyfeldroy/cookiecutter-pypackage", 
         "description": "Cookiecutter template for a Python package"},
        {"name": "django", "url": "https://github.com/pydanny/cookiecutter-django", 
         "description": "Cookiecutter template for Django projects"},
        {"name": "fastapi", "url": "https://github.com/charlax/cookiecutter-python-api", 
         "description": "Cookiecutter template for FastAPI with PostgreSQL"}[15],
    ]
    
    discovered = []
    for template_info in popular_templates:
        if template_info["name"] not in templates:
            await ctx.info(f"Discovered template: {template_info['name']}")
            discovered.append(TemplateInfo(
                name=template_info["name"],
                url=template_info["url"],
                description=template_info["description"],
                is_active=False
            ))
    
    await ctx.info(f"Discovered {len(discovered)} new templates")
    return discovered
```

### MCP Resources

```python
@mcp.resource("templates://list")
async def get_templates_resource() -> List[TemplateInfo]:
    """Get a list of all available cookiecutter templates."""
    return list(templates.values())

@mcp.resource("templates://{name}/variables")
async def get_template_variables_resource(name: str, ctx: Context) -> List[TemplateVariable]:
    """Get the variables for a specific cookiecutter template."""
    return await get_template_variables(name, ctx)

@mcp.resource("templates://{name}/info")
async def get_template_info_resource(name: str) -> TemplateInfo:
    """Get information about a specific cookiecutter template."""
    if name not in templates:
        raise ValueError(f"Template {name} not found")
    return templates[name]
```

### Initialization and Server Launch

```python
# Initialize by loading any saved templates
def load_saved_templates():
    """Load saved templates from the templates directory."""
    for template_file in TEMPLATES_DIR.glob("*.json"):
        try:
            with open(template_file) as f:
                template_data = json.load(f)
                template = TemplateInfo(**template_data)
                templates[template.name] = template
                print(f"Loaded template: {template.name}")
        except Exception as e:
            print(f"Failed to load template from {template_file}: {str(e)}")

# Load saved templates on startup
load_saved_templates()

if __name__ == "__main__":
    # Run the MCP server with SSE transport
    print("Starting Cookiecutter MCP server with SSE transport")
    mcp.run(transport="sse")
```

## Usage Instructions

### Starting the Server

1. Save the code above as `cookiecutter_mcp.py`
2. Install the required dependencies:
   ```bash
   uv pip install fastmcp cookiecutter
   ```
3. Run the server:
   ```bash
   python cookiecutter_mcp.py
   ```

The server will start with SSE transport on the default port (8000). You can now connect to it using any MCP client, including Claude Desktop.

### Using with Claude Desktop

1. Install the server in Claude Desktop:
   ```bash
   fastmcp install cookiecutter_mcp.py --name "Cookiecutter Generator"
   ```

2. Once installed, you can interact with it through Claude:
   ```
   I'd like to create a new Python package using the cookiecutter-pypackage template.
   ```

### Example Workflow

1. Discover available templates:
   ```python
   templates = await client.call_tool("discover_templates")
   ```

2. Add a specific template:
   ```python
   await client.call_tool("add_template", {
       "url": "https://github.com/audreyfeldroy/cookiecutter-pypackage",
       "name": "python-package"
   })
   ```

3. Get template variables:
   ```python
   variables = await client.call_tool("get_template_variables", {
       "template_name": "python-package"
   })
   ```

4. Create a project:
   ```python
   await client.call_tool("create_project", {
       "template_name": "python-package",
       "output_dir": "my-new-project",
       "variables": {
           "project_name": "My Amazing Package",
           "project_slug": "amazing_package",
           "version": "0.1.0"
       }
   })
   ```

## Advanced Features

### Dynamic Template Discovery

The system can discover popular cookiecutter templates using the `discover_templates` tool, which provides recommendations for commonly used templates[12].

### Template Variable Caching

To improve performance, template variables are cached after they're first extracted from the cookiecutter.json file, reducing the need to parse the file repeatedly.

### Isolated Virtual Environments

Each template operates in its own virtual environment, ensuring dependency isolation and preventing conflicts between different cookiecutter templates[9][16].

### Progress Reporting

The MCP context is used for progress reporting, allowing clients to receive real-time updates during template cloning and project generation.

## Extending the System

### Adding Authentication

You can add authentication to protect your MCP server:

```python
from fastmcp.security import BasicAuthMiddleware

mcp.add_middleware(BasicAuthMiddleware(
    username="admin",
    password="secure_password"
))
```

### Supporting Additional Template Sources

Beyond GitHub repositories, you could extend the system to support other template sources:

- Local filesystem templates
- ZIP/tarball archives
- PyPI packages

### Web UI Integration

Create a simple web UI that connects to the SSE endpoint for easier template management:

```python
# Add CORS middleware for web access
from fastmcp.middleware import CORSMiddleware

mcp.add_middleware(CORSMiddleware(
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
))
```

## Conclusion

This FastMCP implementation provides a flexible, dynamic system for working with cookiecutter templates through the Model Context Protocol. By leveraging virtual environments and SSE transport, it offers a clean separation between templates while maintaining a unified interface accessible to both programmatic clients and LLM-powered assistants like Claude.

The system's modular design makes it easy to extend with additional features like authentication, more template sources, or custom hooks for pre/post-processing of generated projects. As the MCP ecosystem continues to evolve, this implementation can be adapted to incorporate new capabilities from both FastMCP and cookiecutter.

Citations:
[1] https://github.com/jlowin/fastmcp
[2] https://cookiecutter.readthedocs.io/en/stable/cookiecutter.html
[3] https://pypi.org/project/venvctl/
[4] https://docs.vultr.com/python/built-in/__import__
[5] https://pypi.org/project/envbuilder/
[6] https://github.com/jlowin/fastmcp
[7] https://mcpmarket.com/server/fastmcp-dynamic-server
[8] https://cookiecutter.readthedocs.io/en/latest/cookiecutter.html
[9] https://virtualenv.pypa.io/en/20.0.7/user_guide.html
[10] https://docs.python.org/es/3.13/library/venv.html
[11] https://pypi.org/project/fastmcp/1.0/
[12] https://github.com/cookiecutter/cookiecutter
[13] https://www.cs.unb.ca/~bremner/teaching/cs2613/books/python3-doc/library/venv.html
[14] https://apidog.com/blog/fastmcp/
[15] https://pypi.org/project/FastAPI-Cookiecutter/
[16] https://virtualenv.pypa.io/en/latest/user_guide.html
[17] https://github.com/charlax/cookiecutter-python-api
[18] https://www.cookiecutter.io
[19] https://betterstack.com/community/questions/how-to-import-python-module-dynamically/
[20] https://www.cookiecutter.io/templates
[21] https://docs.python.org/3/library/venv.html
[22] https://www.geeksforgeeks.org/how-to-dynamically-load-modules-or-classes-in-python/
[23] https://cookiecutter-data-science.drivendata.org
[24] https://gist.github.com/mpurdon/be7f88ee4707f161215187f41c3077f6
[25] https://www.pythonmorsels.com/dynamically-importing-modules/
[26] https://nsls-ii.github.io/scientific-python-cookiecutter/writing-docs.html
[27] https://stackoverflow.com/questions/51287854/python-venv-programmatically
[28] https://docs.python.org/3/library/importlib.html
[29] https://www.reddit.com/r/Python/comments/17k0g04/a_lightweight_cookiecutter_template_for_django/
[30] https://stackoverflow.com/questions/75454139/creating-and-activating-a-virtual-environment-using-a-python-script
[31] https://modelcontextprotocol.io/docs/concepts/tools
[32] https://peps.python.org/pep-0405/
[33] https://github.com/evalstate/fast-agent/discussions/47
[34] https://github.com/python/cpython/issues/122033
[35] https://blog.stackademic.com/build-simple-local-mcp-server-5434d19572a4
[36] https://dev.to/mayankcse/fastmcp-simplifying-ai-context-management-with-the-model-context-protocol-37l9
[37] https://zigabrencic.com/blog/2020-09-18
[38] https://www.firecrawl.dev/blog/fastmcp-tutorial-building-mcp-servers-python
[39] https://www.reddit.com/r/mcp/comments/1h8684w/mcp_graph_memory_server_with_dynamic_tools_and/
[40] https://github.com/python/cpython/blob/main/Lib/venv/__init__.py

---
category,url
Python,"https://github.com/audreyfeldroy/cookiecutter-pypackage"
Python,"https://github.com/cjolowicz/cookiecutter-hypermodern-python"
Data Science,"https://github.com/drivendataorg/cookiecutter-data-science"
Django,"https://github.com/cookiecutter/cookiecutter-django"
Flask,"https://github.com/cookiecutter-flask/cookiecutter-flask"
FastAPI,"https://github.com/arthurhenrique/cookiecutter-fastapi"
React,"https://github.com/vchaptsev/cookiecutter-django-vue"
AWS,"https://github.com/aws-samples/cookiecutter-aws-sam-python"
Machine Learning,"https://github.com/fmind/cookiecutter-mlops-package"
Docker,"https://github.com/docker-science/cookiecutter-docker-science"
Jupyter,"https://github.com/jupyter-widgets/widget-cookiecutter"
Ansible,"https://github.com/iknite/cookiecutter-ansible-role"
Terraform,"https://github.com/TerraformInDepth/terraform-module-cookiecutter"
Rust,"https://github.com/microsoft/cookiecutter-rust-actix-clean-architecture"
Go,"https://github.com/lacion/cookiecutter-golang"
JavaScript,"https://github.com/jupyterlab/extension-cookiecutter-ts"
TypeScript,"https://github.com/jupyterlab/mimerender-cookiecutter-ts"
C++,"https://github.com/ssciwr/cookiecutter-cpp-project"
Qt,"https://github.com/agateau/cookiecutter-qt-app"
PyTorch,"https://github.com/khornlund/cookiecutter-pytorch"
TensorFlow,"https://github.com/tdeboissiere/cookiecutter-deeplearning"
Jupyter Book,"https://github.com/executablebooks/cookiecutter-jupyter-book"
Streamlit,"https://github.com/andymcdgeo/cookiecutter-streamlit"
FastAPI-PostgreSQL,"https://github.com/tiangolo/full-stack-fastapi-postgresql"
Django-REST,"https://github.com/agconti/cookiecutter-django-rest"
Science,"https://github.com/jbusecke/cookiecutter-science-project"
Bioinformatics,"https://github.com/maxplanck-ie/cookiecutter-bioinformatics-project"
LaTeX,"https://github.com/selimb/cookiecutter-latex-article"
Kotlin,"https://github.com/m-x-k/cookiecutter-kotlin-gradle"
Home Assistant,"https://github.com/oncleben31/cookiecutter-homeassistant-custom-component"
.NET,"https://github.com/aws-samples/cookiecutter-aws-sam-dotnet"
Ruby,"https://github.com/customink/cookiecutter-ruby"
Scala,"https://github.com/jpzk/cookiecutter-scala-spark"
Elixir,"https://github.com/mattvonrocketstein/cookiecutter-elixir-project"
R,"https://github.com/associatedpress/cookiecutter-r-project"
Julia,"https://github.com/xtensor-stack/xtensor-julia-cookiecutter"
MATLAB,"https://github.com/gvoysey/cookiecutter-python-scientific"
Arduino,"https://github.com/BrianPugh/cookiecutter-esp32-webserver"
ROS,"https://github.com/ros-industrial/cookiecutter-ros-industrial"
Kubernetes,"https://github.com/uzi0espil/cookiecutter-django-k8s"
Serverless,"https://github.com/ran-isenberg/cookiecutter-serverless-python"
Polars,"https://github.com/MarcoGorelli/cookiecutter-polars-plugins"
ML Research,"https://github.com/csinva/cookiecutter-ml-research"
Education,"https://github.com/mikeckennedy/cookiecutter-course"
Documentation,"https://github.com/pawamoy/cookiecutter-awesome"
Chrome Extension,"https://github.com/audreyfeldroy/cookiecutter-chrome-extension"
Blender,"https://github.com/joshuaskelly/cookiecutter-blender-addon"
Unity,"https://github.com/hackebrot/cookiecutter-kivy"
Godot,"https://github.com/lockie/cookiecutter-lisp-game"
SuperCollider,"https://github.com/supercollider/cookiecutter-supercollider-plugin"
QGIS,"https://github.com/GispoCoding/cookiecutter-qgis-plugin"
WordPress,"https://github.com/Jean-Zombie/cookiecutter-django-wagtail"
Shopify,"https://github.com/awesto/cookiecutter-django-shop"
Moodle,"https://github.com/openedx/edx-cookiecutters"
Salesforce,"https://github.com/datacoves/cookiecutter-dbt"
Zapier,"https://github.com/narfman0/cookiecutter-mobile-backend"
...
