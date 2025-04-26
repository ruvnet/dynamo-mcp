# Dynamo-MCP API Specification

This document provides a detailed specification of the APIs exposed by the dynamo-mcp system, including both external MCP interfaces and internal component interfaces.

## 1. External MCP API

The dynamo-mcp system exposes its functionality through the Model Context Protocol (MCP), providing both tools and resources for clients to interact with.

### 1.1 MCP Tools

#### 1.1.1 Template Management Tools

##### `list_templates()`

Lists all available cookiecutter templates.

**Parameters**: None

**Returns**: 
```json
[
  {
    "name": "string",
    "description": "string",
    "url": "string",
    "venv_path": "string",
    "is_active": true,
    "last_updated": "string"
  }
]
```

**Example**:
```python
templates = await client.call_tool("list_templates")
```

##### `add_template(url, name, description)`

Adds a new cookiecutter template and creates a virtual environment for it.

**Parameters**:
- `url` (string, required): URL of the cookiecutter template repository
- `name` (string, optional): Name for the template (derived from URL if not provided)
- `description` (string, optional): Description of the template

**Returns**:
```json
{
  "name": "string",
  "description": "string",
  "url": "string",
  "venv_path": "string",
  "is_active": true,
  "last_updated": "string"
}
```

**Example**:
```python
template = await client.call_tool("add_template", {
    "url": "https://github.com/audreyfeldroy/cookiecutter-pypackage",
    "name": "python-package",
    "description": "A Python package template"
})
```

##### `update_template(template_name, force)`

Updates a cookiecutter template to the latest version.

**Parameters**:
- `template_name` (string, required): Name of the template to update
- `force` (boolean, optional): Whether to force update even if not needed

**Returns**:
```json
{
  "name": "string",
  "description": "string",
  "url": "string",
  "venv_path": "string",
  "is_active": true,
  "last_updated": "string"
}
```

**Example**:
```python
template = await client.call_tool("update_template", {
    "template_name": "python-package",
    "force": true
})
```

##### `remove_template(template_name)`

Removes a cookiecutter template and its virtual environment.

**Parameters**:
- `template_name` (string, required): Name of the template to remove

**Returns**:
```json
"Template {template_name} removed successfully"
```

**Example**:
```python
result = await client.call_tool("remove_template", {
    "template_name": "python-package"
})
```

##### `discover_templates()`

Discovers popular cookiecutter templates from GitHub.

**Parameters**: None

**Returns**:
```json
[
  {
    "name": "string",
    "description": "string",
    "url": "string",
    "is_active": false
  }
]
```

**Example**:
```python
templates = await client.call_tool("discover_templates")
```

#### 1.1.2 Template Variables Tools

##### `get_template_variables(template_name)`

Gets the variables for a cookiecutter template.

**Parameters**:
- `template_name` (string, required): Name of the template

**Returns**:
```json
[
  {
    "name": "string",
    "description": "string",
    "default": "string",
    "choices": ["string"],
    "required": true,
    "type": "string"
  }
]
```

**Example**:
```python
variables = await client.call_tool("get_template_variables", {
    "template_name": "python-package"
})
```

#### 1.1.3 Project Generation Tools

##### `create_project(request)`

Creates a project from a cookiecutter template.

**Parameters**:
- `request` (object, required):
  - `template_name` (string, required): Name of the template to use
  - `output_dir` (string, required): Directory to output the project to
  - `variables` (object, required): Template variables as key-value pairs

**Returns**:
```json
"Project created successfully in {output_dir}"
```

**Example**:
```python
result = await client.call_tool("create_project", {
    "template_name": "python-package",
    "output_dir": "my-new-project",
    "variables": {
        "project_name": "My Amazing Package",
        "project_slug": "amazing_package",
        "version": "0.1.0"
    }
})
```

### 1.2 MCP Resources

#### 1.2.1 Template Listing Resource

##### `templates://list`

Gets a list of all available cookiecutter templates.

**Parameters**: None

**Returns**:
```json
[
  {
    "name": "string",
    "description": "string",
    "url": "string",
    "venv_path": "string",
    "is_active": true,
    "last_updated": "string"
  }
]
```

**Example**:
```python
templates = await client.access_resource("templates://list")
```

#### 1.2.2 Template Variables Resource

##### `templates://{name}/variables`

Gets the variables for a specific cookiecutter template.

**Parameters**:
- `name` (string, required): Name of the template

**Returns**:
```json
[
  {
    "name": "string",
    "description": "string",
    "default": "string",
    "choices": ["string"],
    "required": true,
    "type": "string"
  }
]
```

**Example**:
```python
variables = await client.access_resource("templates://python-package/variables")
```

#### 1.2.3 Template Information Resource

##### `templates://{name}/info`

Gets information about a specific cookiecutter template.

**Parameters**:
- `name` (string, required): Name of the template

**Returns**:
```json
{
  "name": "string",
  "description": "string",
  "url": "string",
  "venv_path": "string",
  "is_active": true,
  "last_updated": "string"
}
```

**Example**:
```python
template = await client.access_resource("templates://python-package/info")
```

## 2. Internal Component APIs

### 2.1 Template Registry Manager API

#### 2.1.1 Public Methods

##### `list_templates() -> List[TemplateInfo]`

Lists all available cookiecutter templates.

**Returns**: List of TemplateInfo objects

##### `add_template(url: str, ctx: Context, name: Optional[str] = None, description: Optional[str] = None) -> TemplateInfo`

Adds a new cookiecutter template and creates a virtual environment for it.

**Parameters**:
- `url` (str): URL of the cookiecutter template repository
- `ctx` (Context): MCP context for progress reporting
- `name` (Optional[str]): Name for the template (derived from URL if not provided)
- `description` (Optional[str]): Description of the template

**Returns**: TemplateInfo object for the added template

##### `update_template(template_name: str, ctx: Context, force: bool = False) -> TemplateInfo`

Updates a cookiecutter template to the latest version.

**Parameters**:
- `template_name` (str): Name of the template to update
- `ctx` (Context): MCP context for progress reporting
- `force` (bool): Whether to force update even if not needed

**Returns**: TemplateInfo object for the updated template

##### `remove_template(template_name: str, ctx: Context) -> str`

Removes a cookiecutter template and its virtual environment.

**Parameters**:
- `template_name` (str): Name of the template to remove
- `ctx` (Context): MCP context for progress reporting

**Returns**: Success message

##### `discover_templates(ctx: Context) -> List[TemplateInfo]`

Discovers popular cookiecutter templates from GitHub.

**Parameters**:
- `ctx` (Context): MCP context for progress reporting

**Returns**: List of discovered TemplateInfo objects

#### 2.1.2 Private Methods

##### `_save_template_info(template: TemplateInfo) -> None`

Saves template information to disk.

**Parameters**:
- `template` (TemplateInfo): Template information to save

##### `_load_saved_templates() -> Dict[str, TemplateInfo]`

Loads saved templates from disk.

**Returns**: Dictionary mapping template names to TemplateInfo objects

### 2.2 Virtual Environment Manager API

#### 2.2.1 Public Methods

None (all methods are private and used internally)

#### 2.2.2 Private Methods

##### `_create_venv(path: Path) -> None`

Creates a new virtual environment.

**Parameters**:
- `path` (Path): Path to create the virtual environment at

##### `_run_in_venv(venv_path: Path, cmd: List[str], ctx: Optional[Context] = None) -> str`

Runs a command in a virtual environment.

**Parameters**:
- `venv_path` (Path): Path to the virtual environment
- `cmd` (List[str]): Command to run
- `ctx` (Optional[Context]): MCP context for progress reporting

**Returns**: Command output as string

##### `_cleanup_venv(path: Path) -> None`

Removes a virtual environment.

**Parameters**:
- `path` (Path): Path to the virtual environment to remove

### 2.3 Interface Generator API

#### 2.3.1 Public Methods

##### `get_template_variables(template_name: str, ctx: Context) -> List[TemplateVariable]`

Gets the variables for a cookiecutter template.

**Parameters**:
- `template_name` (str): Name of the template
- `ctx` (Context): MCP context for progress reporting

**Returns**: List of TemplateVariable objects

#### 2.3.2 Private Methods

##### `_get_template_variables(template_dir: Path) -> List[TemplateVariable]`

Extracts variables from a cookiecutter.json file.

**Parameters**:
- `template_dir` (Path): Path to the template directory

**Returns**: List of TemplateVariable objects

### 2.4 Project Generator API

#### 2.4.1 Public Methods

##### `create_project(request: CreateProjectRequest, ctx: Context) -> str`

Creates a project from a cookiecutter template.

**Parameters**:
- `request` (CreateProjectRequest): Project creation request
- `ctx` (Context): MCP context for progress reporting

**Returns**: Success message

#### 2.4.2 Private Methods

None

## 3. Data Models

### 3.1 TemplateInfo

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

### 3.2 TemplateVariable

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

### 3.3 CreateProjectRequest

```python
class CreateProjectRequest(BaseModel):
    """Request to create a project from a template."""
    template_name: str
    output_dir: str
    variables: Dict[str, Any]
```

## 4. Error Handling

### 4.1 Error Types

| Error Type | HTTP Status | Description |
|------------|-------------|-------------|
| ValidationError | 400 | Invalid input parameters |
| TemplateNotFoundError | 404 | Template does not exist |
| EnvironmentError | 500 | Virtual environment issues |
| CookiecutterError | 500 | Template generation failures |
| IOError | 500 | File system operation failures |

### 4.2 Error Response Format

```json
{
  "error": {
    "type": "string",
    "message": "string",
    "details": {}
  }
}
```

## 5. Authentication (Optional)

If authentication is enabled, all API endpoints require authentication using one of the following methods:

### 5.1 Basic Authentication

```
Authorization: Basic <base64-encoded-credentials>
```

### 5.2 API Key Authentication

```
Authorization: Bearer <api-key>
```

## 6. Rate Limiting

To prevent abuse, the API may implement rate limiting:

- Maximum 100 requests per minute per client
- Maximum 10 concurrent template operations
- Maximum 5 concurrent project generations

Rate limit headers are included in responses:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1619712000
```

## 7. SSE Event Format

The SSE transport uses the following event format:

```
event: <event-type>
data: <json-data>

```

### 7.1 Event Types

| Event Type | Description | Data Format |
|------------|-------------|-------------|
| `info` | Informational message | `{"message": "string"}` |
| `progress` | Progress update | `{"message": "string", "percent": number}` |
| `error` | Error message | `{"message": "string", "type": "string"}` |
| `result` | Operation result | `{"result": any}` |

### 7.2 Example SSE Stream

```
event: info
data: {"message": "Adding template python-package"}

event: progress
data: {"message": "Creating virtual environment", "percent": 25}

event: progress
data: {"message": "Installing cookiecutter", "percent": 50}

event: progress
data: {"message": "Cloning template", "percent": 75}

event: result
data: {"result": {"name": "python-package", "description": "A Python package template", "url": "https://github.com/audreyfeldroy/cookiecutter-pypackage", "venv_path": "venvs/python-package", "is_active": true, "last_updated": "2023-04-01T12:00:00"}}
```

## 8. Client Integration Examples

### 8.1 Python Client

```python
from fastmcp.client import MCPClient

async def main():
    # Connect to the MCP server
    client = MCPClient("http://localhost:8000")
    
    # List available templates
    templates = await client.call_tool("list_templates")
    print(f"Available templates: {templates}")
    
    # Add a template
    template = await client.call_tool("add_template", {
        "url": "https://github.com/audreyfeldroy/cookiecutter-pypackage",
        "name": "python-package"
    })
    print(f"Added template: {template}")
    
    # Get template variables
    variables = await client.call_tool("get_template_variables", {
        "template_name": "python-package"
    })
    print(f"Template variables: {variables}")
    
    # Create a project
    result = await client.call_tool("create_project", {
        "template_name": "python-package",
        "output_dir": "my-new-project",
        "variables": {
            "project_name": "My Amazing Package",
            "project_slug": "amazing_package",
            "version": "0.1.0"
        }
    })
    print(f"Project creation result: {result}")
```

### 8.2 JavaScript Client

```javascript
import { EventSource } from 'eventsource';

class MCPClient {
  constructor(baseUrl) {
    this.baseUrl = baseUrl;
  }
  
  async callTool(toolName, params = {}) {
    return new Promise((resolve, reject) => {
      const url = `${this.baseUrl}/tools/${toolName}`;
      const source = new EventSource(url);
      
      source.addEventListener('result', (event) => {
        const data = JSON.parse(event.data);
        source.close();
        resolve(data.result);
      });
      
      source.addEventListener('error', (event) => {
        const data = JSON.parse(event.data);
        source.close();
        reject(new Error(data.message));
      });
      
      // Send parameters
      fetch(`${url}/params`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(params)
      });
    });
  }
}

// Example usage
async function main() {
  const client = new MCPClient('http://localhost:8000');
  
  // List available templates
  const templates = await client.callTool('list_templates');
  console.log('Available templates:', templates);
  
  // Add a template
  const template = await client.callTool('add_template', {
    url: 'https://github.com/audreyfeldroy/cookiecutter-pypackage',
    name: 'python-package'
  });
  console.log('Added template:', template);
}

main().catch(console.error);
```

## 9. Conclusion

This API specification provides a comprehensive guide to the interfaces exposed by the dynamo-mcp system. By following these specifications, clients can interact with the system to manage cookiecutter templates and generate projects.

The MCP-based design allows for seamless integration with LLM-powered applications like Claude, while the SSE transport enables real-time progress reporting and updates. The modular internal APIs facilitate component-based development and testing.