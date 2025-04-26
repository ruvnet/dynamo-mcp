# Dynamo-MCP System Architecture

## 1. System Overview

The dynamo-mcp system is a dynamic MCP (Model Context Protocol) registry that manages cookiecutter templates. It discovers, loads, and exposes these templates as MCP tools and resources, allowing clients (particularly LLM-powered applications like Claude) to interact with them through a unified interface.

Key capabilities include:
- Template discovery and management
- Isolated virtual environments for each template
- Dynamic interface generation based on template configuration
- Real-time communication via Server-Sent Events (SSE)
- Unified MCP-compatible API

## 2. Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                       DYNAMO-MCP SYSTEM                                         │
│                                                                                                 │
│  ┌───────────────────────┐                                      ┌───────────────────────────┐   │
│  │                       │                                      │                           │   │
│  │   Template Registry   │◄────────────────────────────────────┤   Template Repository     │   │
│  │   Manager             │                                      │   (templates/*.json)      │   │
│  │                       │                                      │                           │   │
│  └───────────┬───────────┘                                      └───────────────────────────┘   │
│              │                                                                                  │
│              │ manages                                                                          │
│              ▼                                                                                  │
│  ┌───────────────────────┐    creates/manages     ┌───────────────────────────┐                │
│  │                       │◄─────────────────────►│                           │                │
│  │   Virtual Environment │                        │   Environment Repository  │                │
│  │   Manager             │                        │   (venvs/*)               │                │
│  │                       │                        │                           │                │
│  └───────────┬───────────┘                        └───────────────────────────┘                │
│              │                                                                                  │
│              │ executes                                                                         │
│              ▼                                                                                  │
│  ┌───────────────────────┐    extracts           ┌───────────────────────────┐                │
│  │                       │◄─────────────────────►│                           │                │
│  │   Interface Generator │                        │   Template Variables      │                │
│  │                       │                        │   Cache                   │                │
│  │                       │                        │                           │                │
│  └───────────┬───────────┘                        └───────────────────────────┘                │
│              │                                                                                  │
│              │ provides                                                                         │
│              ▼                                                                                  │
│  ┌───────────────────────┐                        ┌───────────────────────────┐                │
│  │                       │    generates          │                           │                │
│  │   MCP Server          │◄─────────────────────►│   Project Generator       │                │
│  │   (FastMCP)           │                        │   (outputs/*)             │                │
│  │                       │                        │                           │                │
│  └───────────┬───────────┘                        └───────────────────────────┘                │
│              │                                                                                  │
└──────────────┼──────────────────────────────────────────────────────────────────────────────────┘
               │
               │ communicates via SSE
               ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                      SSE TRANSPORT LAYER                                         │
└──────────────┬───────────────────────────────────────────────────────────────────────────────────┘
               │
               │ connects to
               ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                           CLIENTS                                                │
│                                                                                                  │
│  ┌───────────────────────┐    ┌───────────────────────────┐    ┌───────────────────────────┐    │
│  │                       │    │                           │    │                           │    │
│  │   LLM Applications    │    │   Web UI Clients          │    │   API Clients             │    │
│  │   (Claude, etc.)      │    │                           │    │                           │    │
│  │                       │    │                           │    │                           │    │
│  └───────────────────────┘    └───────────────────────────┘    └───────────────────────────┘    │
│                                                                                                  │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

## 3. Core Components

### 3.1 Template Registry Manager

**Purpose**: Central component responsible for discovering, registering, and managing cookiecutter templates.

**Responsibilities**:
- Template discovery from various sources (GitHub, local filesystem)
- Template registration and metadata management
- Template versioning and updates
- Template removal and cleanup

**Key Classes**:
```python
class TemplateInfo:
    name: str                # Template name
    description: str         # Template description
    url: str                 # Source URL
    venv_path: Optional[str] # Path to virtual environment
    is_active: bool          # Whether template is ready for use
    last_updated: Optional[str] # Last update timestamp
    variables_cache: Optional[List[Dict[str, Any]]] # Cached template variables
```

**Key Methods**:
- `list_templates()`: List all available templates
- `add_template(url, name, description)`: Add a new template
- `update_template(template_name)`: Update an existing template
- `remove_template(template_name)`: Remove a template
- `discover_templates()`: Discover popular templates

### 3.2 Virtual Environment Manager

**Purpose**: Creates and manages isolated virtual environments for each template.

**Responsibilities**:
- Virtual environment creation with proper dependencies
- Environment isolation to prevent conflicts
- Command execution within specific environments
- Environment cleanup and resource management

**Key Methods**:
- `_create_venv(path)`: Create a new virtual environment
- `_run_in_venv(venv_path, cmd)`: Run a command in a specific environment
- `_cleanup_venv(venv_path)`: Remove a virtual environment

**Implementation Details**:
- Uses Python's built-in `venv` module
- Maintains separate directories for each template environment
- Handles platform-specific differences (Windows/Unix)

### 3.3 Interface Generator

**Purpose**: Dynamically generates MCP interfaces from cookiecutter template configurations.

**Responsibilities**:
- Extract variables from cookiecutter.json files
- Convert template variables to MCP-compatible formats
- Generate schema definitions for template parameters
- Cache variable definitions for performance

**Key Classes**:
```python
class TemplateVariable:
    name: str                # Variable name
    description: str         # Variable description
    default: Optional[str]   # Default value
    choices: Optional[List[str]] # Possible choices for selection
    required: bool           # Whether variable is required
    type: str                # Data type (string, boolean, number, choice)
```

**Key Methods**:
- `_get_template_variables(template_dir)`: Extract variables from cookiecutter.json
- `get_template_variables(template_name)`: Get variables for a template

### 3.4 MCP Server

**Purpose**: Exposes template functionality through the Model Context Protocol.

**Responsibilities**:
- Registers MCP tools for template operations
- Exposes MCP resources for template data
- Handles context management for operations
- Provides progress reporting during operations

**Key Classes**:
```python
class CreateProjectRequest:
    template_name: str       # Template to use
    output_dir: str          # Output directory
    variables: Dict[str, Any] # Template variables
```

**MCP Tools**:
- `list_templates()`: List all available templates
- `get_template_variables(template_name)`: Get variables for a template
- `add_template(url, name, description)`: Add a new template
- `create_project(request)`: Create a project from a template
- `update_template(template_name)`: Update a template
- `remove_template(template_name)`: Remove a template
- `discover_templates()`: Discover popular templates

**MCP Resources**:
- `templates://list`: List of all templates
- `templates://{name}/variables`: Variables for a specific template
- `templates://{name}/info`: Information about a specific template

### 3.5 Project Generator

**Purpose**: Generates projects from templates using the cookiecutter engine.

**Responsibilities**:
- Prepare variables for cookiecutter
- Execute cookiecutter in the appropriate environment
- Manage output directories
- Report generation progress

**Key Methods**:
- `create_project(template_name, output_dir, variables)`: Generate a project

### 3.6 SSE Transport Layer

**Purpose**: Enables real-time communication with clients using Server-Sent Events.

**Responsibilities**:
- Establish persistent connections with clients
- Stream operation progress and results
- Handle connection management and error recovery
- Provide web-compatible communication channel

## 4. Data Flow

### 4.1 Template Registration Flow

1. Client requests template registration with a URL
2. Template Registry Manager validates the template source
3. Virtual Environment Manager creates an isolated environment
4. Cookiecutter is installed in the environment
5. Template is cloned into the environment
6. Interface Generator extracts variables from cookiecutter.json
7. Template metadata is stored in the Template Repository
8. MCP Server exposes the new template as tools and resources
9. Client receives confirmation via SSE

```
┌─────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│         │     │                 │     │                 │     │                 │
│ Client  │────►│ Template        │────►│ Virtual Env     │────►│ Interface       │
│         │     │ Registry        │     │ Manager         │     │ Generator       │
│         │     │                 │     │                 │     │                 │
└─────────┘     └─────────────────┘     └─────────────────┘     └─────────────────┘
                        │                       │                        │
                        ▼                       ▼                        ▼
                ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
                │                 │     │                 │     │                 │
                │ Template        │     │ Environment     │     │ Template        │
                │ Repository      │     │ Repository      │     │ Variables Cache │
                │                 │     │                 │     │                 │
                └─────────────────┘     └─────────────────┘     └─────────────────┘
```

### 4.2 Project Creation Flow

1. Client requests project creation with template name and variables
2. MCP Server validates the request
3. Template Registry Manager retrieves template information
4. Virtual Environment Manager prepares the environment
5. Project Generator executes cookiecutter in the isolated environment
6. Progress is reported through SSE Transport Layer
7. Generated project is made available to the client

```
┌─────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│         │     │                 │     │                 │     │                 │
│ Client  │────►│ MCP Server      │────►│ Template        │────►│ Virtual Env     │
│         │     │                 │     │ Registry        │     │ Manager         │
│         │     │                 │     │                 │     │                 │
└─────────┘     └─────────────────┘     └─────────────────┘     └─────────────────┘
    ▲                                                                   │
    │                                                                   ▼
    │                                                           ┌─────────────────┐
    │                                                           │                 │
    └───────────────────────────────────────────────────────────┤ Project         │
                                                                │ Generator       │
                                                                │                 │
                                                                └─────────────────┘
```

## 5. API Interfaces

### 5.1 MCP Tools API

```python
# Template Management
list_templates() -> List[TemplateInfo]
add_template(url: str, name: Optional[str], description: Optional[str]) -> TemplateInfo
update_template(template_name: str, force: bool) -> TemplateInfo
remove_template(template_name: str) -> str
discover_templates() -> List[TemplateInfo]

# Template Variables
get_template_variables(template_name: str) -> List[TemplateVariable]

# Project Generation
create_project(request: CreateProjectRequest) -> str
```

### 5.2 MCP Resources API

```
# Template Listing
templates://list -> List[TemplateInfo]

# Template Variables
templates://{name}/variables -> List[TemplateVariable]

# Template Information
templates://{name}/info -> TemplateInfo
```

### 5.3 Internal API

```python
# Virtual Environment Management
_create_venv(path: Path) -> None
_run_in_venv(venv_path: Path, cmd: List[str]) -> str

# Template Variable Extraction
_get_template_variables(template_dir: Path) -> List[TemplateVariable]

# File System Operations
_save_template_info(template: TemplateInfo) -> None
_load_saved_templates() -> Dict[str, TemplateInfo]
```

## 6. Storage Structure

```
dynamo-mcp/
├── venvs/                  # Virtual environments
│   ├── template1/          # Environment for template1
│   │   ├── bin/            # Environment executables
│   │   └── template/       # Cloned template
│   └── template2/          # Environment for template2
│
├── templates/              # Template metadata
│   ├── template1.json      # Metadata for template1
│   └── template2.json      # Metadata for template2
│
├── outputs/                # Generated projects
│   ├── project1/           # Output from template1
│   └── project2/           # Output from template2
│
└── cookiecutter_mcp.py     # Main server implementation
```

## 7. Security Considerations

1. **Input Validation**: All template URLs and variables are validated before use
2. **Environment Isolation**: Each template runs in its own virtual environment
3. **Resource Limits**: Prevent excessive resource consumption by templates
4. **Authentication**: Optional authentication for MCP server access
5. **Sandboxing**: Limit template execution capabilities

## 8. Extensibility Points

1. **Template Sources**: Support for additional template sources beyond GitHub
   - Local filesystem templates
   - ZIP/tarball archives
   - PyPI packages

2. **Authentication Providers**: Pluggable authentication mechanisms
   - Basic authentication
   - API key authentication
   - OAuth integration

3. **Transport Layers**: Alternative transport mechanisms beyond SSE
   - WebSockets
   - HTTP long polling
   - gRPC streaming

4. **Template Hooks**: Pre/post-processing hooks for templates
   - Custom variable validation
   - Post-generation processing
   - Integration with external tools

5. **UI Integration**: Web UI components for template management
   - Template browser
   - Variable editor
   - Project viewer

## 9. Implementation Roadmap

### Phase 1: Core Functionality
- Template Registry Manager implementation
- Virtual Environment Manager implementation
- Basic MCP Server with SSE transport
- Project Generator for simple templates

### Phase 2: Enhanced Features
- Dynamic Interface Generator with variable type inference
- Template discovery and recommendations
- Variable caching and optimization
- Improved error handling and reporting

### Phase 3: Advanced Capabilities
- Authentication and security enhancements
- Web UI integration
- Extended template sources
- Template hooks and customization
- Performance optimizations

## 10. Conclusion

The dynamo-mcp architecture provides a flexible, extensible system for managing cookiecutter templates through the Model Context Protocol. By leveraging isolated virtual environments and dynamic interface generation, it enables seamless integration with LLM-powered applications while maintaining security and performance.

The modular design allows for future enhancements and extensions, such as additional template sources, authentication mechanisms, and user interfaces, while the core functionality remains focused on template management, environment isolation, and MCP compatibility.