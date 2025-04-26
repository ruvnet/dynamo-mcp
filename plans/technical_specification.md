# Dynamo-MCP Technical Specification

This document provides detailed technical specifications for implementing the dynamo-mcp system, a dynamic MCP registry using Cookiecutter templates.

## 1. System Requirements

### 1.1 Functional Requirements

- Discover, add, update, and remove cookiecutter templates
- Create isolated virtual environments for each template
- Extract template variables and generate dynamic interfaces
- Expose templates as MCP tools and resources
- Generate projects from templates with user-provided variables
- Communicate with clients through SSE transport

### 1.2 Non-Functional Requirements

- **Performance**: Fast template registration and project generation
- **Scalability**: Support for multiple templates and concurrent clients
- **Security**: Isolated environments and input validation
- **Reliability**: Robust error handling and recovery
- **Usability**: Simple API for LLM integration

### 1.3 Dependencies

- Python 3.8+
- FastMCP library
- Cookiecutter
- Pydantic
- AsyncIO

## 2. Component Specifications

### 2.1 Template Registry Manager

#### 2.1.1 Data Models

```python
class TemplateInfo(BaseModel):
    """Information about a cookiecutter template."""
    name: str
    description: str
    url: str
    venv_path: Optional[str] = None
    is_active: bool = False
    last_updated: Optional[str] = None
    variables_cache: Optional[List[Dict[str, Any]]] = Field(default=None, exclude=True)
```

#### 2.1.2 Storage

Templates are stored in two places:
1. In-memory dictionary for fast access
2. JSON files in the `templates/` directory for persistence

#### 2.1.3 Key Functions

```python
async def list_templates() -> List[TemplateInfo]:
    """List all available cookiecutter templates."""
    return list(templates.values())

async def add_template(url: str, ctx: Context, name: Optional[str] = None, 
                      description: Optional[str] = None) -> TemplateInfo:
    """Add a new cookiecutter template and create a virtual environment for it."""
    # Implementation details:
    # 1. Extract name from URL if not provided
    # 2. Create template info object
    # 3. Create virtual environment
    # 4. Install cookiecutter
    # 5. Clone template
    # 6. Extract variables
    # 7. Save template info
    # 8. Return template info

async def update_template(template_name: str, ctx: Context, force: bool = False) -> TemplateInfo:
    """Update a cookiecutter template to the latest version."""
    # Implementation details:
    # 1. Validate template exists
    # 2. Re-add template to update it

async def remove_template(template_name: str, ctx: Context) -> str:
    """Remove a cookiecutter template and its virtual environment."""
    # Implementation details:
    # 1. Validate template exists
    # 2. Remove virtual environment
    # 3. Remove template info file
    # 4. Remove from in-memory storage
    # 5. Return success message

async def discover_templates(ctx: Context) -> List[TemplateInfo]:
    """Discover popular cookiecutter templates from GitHub."""
    # Implementation details:
    # 1. Define list of popular templates
    # 2. Filter out already installed templates
    # 3. Return discovered templates
```

### 2.2 Virtual Environment Manager

#### 2.2.1 Environment Structure

Each template has its own virtual environment in the `venvs/` directory:

```
venvs/
└── template_name/
    ├── bin/              # Unix executables
    ├── Scripts/          # Windows executables
    ├── Lib/              # Python libraries
    └── template/         # Cloned template
```

#### 2.2.2 Key Functions

```python
async def _run_in_venv(venv_path: Path, cmd: List[str], ctx: Optional[Context] = None) -> str:
    """Run a command in a virtual environment."""
    # Implementation details:
    # 1. Determine Python path based on OS
    # 2. Construct command string
    # 3. Log command if context provided
    # 4. Create subprocess
    # 5. Capture stdout and stderr
    # 6. Handle errors
    # 7. Return stdout

def _create_venv(path: Path) -> None:
    """Create a new virtual environment."""
    # Implementation details:
    # 1. Remove existing environment if present
    # 2. Create new environment with pip
    # 3. Install required dependencies

async def _cleanup_venv(path: Path) -> None:
    """Remove a virtual environment."""
    # Implementation details:
    # 1. Check if path exists
    # 2. Remove directory recursively
```

### 2.3 Interface Generator

#### 2.3.1 Data Models

```python
class TemplateVariable(BaseModel):
    """A variable for a cookiecutter template."""
    name: str
    description: str
    default: Optional[str] = None
    choices: Optional[List[str]] = None
    required: bool = True
    type: str = "string"
```

#### 2.3.2 Key Functions

```python
async def _get_template_variables(template_dir: Path) -> List[TemplateVariable]:
    """Extract variables from a cookiecutter.json file."""
    # Implementation details:
    # 1. Locate cookiecutter.json file
    # 2. Load JSON content
    # 3. Process each key-value pair
    # 4. Determine variable type and defaults
    # 5. Create TemplateVariable objects
    # 6. Return list of variables

async def get_template_variables(template_name: str, ctx: Context) -> List[TemplateVariable]:
    """Get the variables for a cookiecutter template."""
    # Implementation details:
    # 1. Validate template exists
    # 2. Check for cached variables
    # 3. If not cached, extract variables
    # 4. Cache variables for future use
    # 5. Return variables
```

### 2.4 Project Generator

#### 2.4.1 Data Models

```python
class CreateProjectRequest(BaseModel):
    """Request to create a project from a template."""
    template_name: str
    output_dir: str
    variables: Dict[str, Any]
```

#### 2.4.2 Key Functions

```python
async def create_project(request: CreateProjectRequest, ctx: Context) -> str:
    """Create a project from a cookiecutter template."""
    # Implementation details:
    # 1. Validate template exists
    # 2. Prepare output directory
    # 3. Create config file with variables
    # 4. Run cookiecutter in virtual environment
    # 5. Clean up temporary files
    # 6. Return success message
```

### 2.5 MCP Server

#### 2.5.1 Server Configuration

```python
# Main FastMCP server
mcp = FastMCP("Cookiecutter Templates", dependencies=["cookiecutter"])

# Register tools
mcp.tool()(list_templates)
mcp.tool()(get_template_variables)
mcp.tool()(add_template)
mcp.tool()(update_template)
mcp.tool()(remove_template)
mcp.tool()(discover_templates)
mcp.tool()(create_project)

# Register resources
mcp.resource("templates://list")(get_templates_resource)
mcp.resource("templates://{name}/variables")(get_template_variables_resource)
mcp.resource("templates://{name}/info")(get_template_info_resource)
```

#### 2.5.2 SSE Transport

The server uses Server-Sent Events (SSE) for real-time communication with clients:

```python
if __name__ == "__main__":
    # Run the MCP server with SSE transport
    print("Starting Cookiecutter MCP server with SSE transport")
    mcp.run(transport="sse")
```

## 3. Interaction Protocols

### 3.1 Template Registration Protocol

```
Client                                Server
  |                                     |
  |  Request to add template            |
  | ----------------------------------> |
  |                                     |  Create virtual environment
  |                                     |  Install cookiecutter
  |                                     |  Clone template
  |                                     |  Extract variables
  |                                     |  Save template info
  |  SSE progress updates               |
  | <---------------------------------- |
  |                                     |
  |  Template added successfully        |
  | <---------------------------------- |
  |                                     |
```

### 3.2 Project Creation Protocol

```
Client                                Server
  |                                     |
  |  Request to create project          |
  | ----------------------------------> |
  |                                     |  Validate template
  |                                     |  Prepare variables
  |                                     |  Run cookiecutter
  |                                     |  Generate project
  |  SSE progress updates               |
  | <---------------------------------- |
  |                                     |
  |  Project created successfully       |
  | <---------------------------------- |
  |                                     |
```

## 4. Error Handling

### 4.1 Error Types

1. **ValidationError**: Invalid input parameters
2. **TemplateNotFoundError**: Template does not exist
3. **EnvironmentError**: Virtual environment issues
4. **CookiecutterError**: Template generation failures
5. **IOError**: File system operation failures

### 4.2 Error Reporting

Errors are reported through the MCP context:

```python
try:
    # Operation that might fail
    result = await some_operation()
    return result
except Exception as e:
    await ctx.error(f"Operation failed: {str(e)}")
    raise
```

## 5. Security Measures

### 5.1 Input Validation

All user inputs are validated using Pydantic models:

```python
class CreateProjectRequest(BaseModel):
    template_name: str
    output_dir: str
    variables: Dict[str, Any]
```

### 5.2 Environment Isolation

Each template runs in its own virtual environment to prevent conflicts and limit security risks.

### 5.3 Resource Limits

To prevent abuse, the system can implement resource limits:

```python
# Example resource limits
MAX_TEMPLATES = 50
MAX_PROJECT_SIZE = 1024 * 1024 * 100  # 100 MB
TIMEOUT = 60  # 60 seconds
```

### 5.4 Authentication (Optional)

```python
from fastmcp.security import BasicAuthMiddleware

mcp.add_middleware(BasicAuthMiddleware(
    username="admin",
    password="secure_password"
))
```

## 6. Performance Considerations

### 6.1 Caching

Template variables are cached to improve performance:

```python
# Check if we have cached variables
if template.variables_cache:
    return [TemplateVariable(**v) for v in template.variables_cache]
```

### 6.2 Asynchronous Operations

All operations are asynchronous to improve concurrency:

```python
async def add_template(url: str, ctx: Context, name: Optional[str] = None, 
                      description: Optional[str] = None) -> TemplateInfo:
    # Asynchronous implementation
```

### 6.3 Lazy Loading

Templates are loaded on demand to reduce startup time.

## 7. Testing Strategy

### 7.1 Unit Tests

```python
# Example unit test for template variable extraction
async def test_get_template_variables():
    # Setup test environment
    template_dir = Path("./test_templates/sample")
    
    # Create test cookiecutter.json
    os.makedirs(template_dir, exist_ok=True)
    with open(template_dir / "cookiecutter.json", "w") as f:
        json.dump({
            "project_name": "Sample Project",
            "version": "0.1.0",
            "use_pytest": ["y", "n"]
        }, f)
    
    # Call function
    variables = await _get_template_variables(template_dir)
    
    # Assertions
    assert len(variables) == 3
    assert variables[0].name == "project_name"
    assert variables[0].default == "Sample Project"
    assert variables[2].choices == ["y", "n"]
    assert variables[2].type == "choice"
```

### 7.2 Integration Tests

```python
# Example integration test for template addition
async def test_add_template():
    # Setup test context
    ctx = MockContext()
    
    # Call function
    template = await add_template(
        "https://github.com/audreyfeldroy/cookiecutter-pypackage",
        ctx,
        "test-template",
        "Test template"
    )
    
    # Assertions
    assert template.name == "test-template"
    assert template.is_active == True
    assert Path(template.venv_path).exists()
    
    # Cleanup
    await remove_template("test-template", ctx)
```

### 7.3 End-to-End Tests

```python
# Example end-to-end test for project creation
async def test_create_project():
    # Setup test context
    ctx = MockContext()
    
    # Add template
    await add_template(
        "https://github.com/audreyfeldroy/cookiecutter-pypackage",
        ctx,
        "test-template",
        "Test template"
    )
    
    # Create project
    result = await create_project(
        CreateProjectRequest(
            template_name="test-template",
            output_dir="test-output",
            variables={
                "project_name": "Test Project",
                "project_slug": "test_project",
                "version": "0.1.0"
            }
        ),
        ctx
    )
    
    # Assertions
    assert "Project created successfully" in result
    assert Path("test-output/test_project").exists()
    assert Path("test-output/test_project/setup.py").exists()
    
    # Cleanup
    shutil.rmtree("test-output")
    await remove_template("test-template", ctx)
```

## 8. Deployment

### 8.1 Local Deployment

```bash
# Install dependencies
pip install fastmcp cookiecutter pydantic

# Run server
python cookiecutter_mcp.py
```

### 8.2 Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "cookiecutter_mcp.py"]
```

### 8.3 Claude Desktop Integration

```bash
# Install server in Claude Desktop
fastmcp install cookiecutter_mcp.py --name "Cookiecutter Generator"
```

## 9. Future Extensions

### 9.1 Additional Template Sources

```python
async def add_template_from_zip(zip_file: str, ctx: Context) -> TemplateInfo:
    """Add a template from a ZIP file."""
    # Implementation details
```

### 9.2 Web UI

```python
# Add CORS middleware for web access
from fastmcp.middleware import CORSMiddleware

mcp.add_middleware(CORSMiddleware(
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
))
```

### 9.3 Template Hooks

```python
class TemplateHook(BaseModel):
    """Hook for pre/post-processing of templates."""
    name: str
    event: str  # "pre" or "post"
    script: str
```

## 10. Conclusion

This technical specification provides a comprehensive guide for implementing the dynamo-mcp system. By following these specifications, developers can create a robust, secure, and performant system for managing cookiecutter templates through the Model Context Protocol.

The modular design allows for easy extension and customization, while the focus on security and performance ensures a reliable system for both programmatic clients and LLM-powered applications.