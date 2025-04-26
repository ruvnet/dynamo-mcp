# Dynamo-MCP Component Diagram

This document provides a detailed component diagram for the dynamo-mcp system, illustrating the relationships and interactions between the various components.

## System Component Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                       DYNAMO-MCP SYSTEM                                         │
│                                                                                                 │
│  ┌───────────────────────┐                                      ┌───────────────────────────┐   │
│  │  Template Registry    │◄────────────────────────────────────┤   Template Repository     │   │
│  │  Manager              │                                      │   (templates/*.json)      │   │
│  │                       │                                      │                           │   │
│  │  - list_templates()   │                                      │  - TemplateInfo objects   │   │
│  │  - add_template()     │                                      │  - Metadata storage       │   │
│  │  - update_template()  │                                      │  - Version tracking       │   │
│  │  - remove_template()  │                                      │                           │   │
│  │  - discover_templates()│                                     └───────────────────────────┘   │
│  └───────────┬───────────┘                                                                      │
│              │                                                                                  │
│              │ manages                                                                          │
│              ▼                                                                                  │
│  ┌───────────────────────┐    creates/manages     ┌───────────────────────────┐                │
│  │  Virtual Environment  │◄─────────────────────►│   Environment Repository  │                │
│  │  Manager              │                        │   (venvs/*)               │                │
│  │                       │                        │                           │                │
│  │  - _create_venv()     │                        │  - Isolated environments  │                │
│  │  - _run_in_venv()     │                        │  - Template clones        │                │
│  │  - _cleanup_venv()    │                        │  - Cookiecutter installs  │                │
│  │                       │                        │                           │                │
│  └───────────┬───────────┘                        └───────────────────────────┘                │
│              │                                                                                  │
│              │ executes                                                                         │
│              ▼                                                                                  │
│  ┌───────────────────────┐    extracts           ┌───────────────────────────┐                │
│  │  Interface Generator  │◄─────────────────────►│   Template Variables      │                │
│  │                       │                        │   Cache                   │                │
│  │  - _get_template_     │                        │                           │                │
│  │    variables()        │                        │  - TemplateVariable       │                │
│  │  - get_template_      │                        │    objects                │                │
│  │    variables()        │                        │  - Type information       │                │
│  │                       │                        │  - Default values         │                │
│  └───────────┬───────────┘                        └───────────────────────────┘                │
│              │                                                                                  │
│              │ provides                                                                         │
│              ▼                                                                                  │
│  ┌───────────────────────┐                        ┌───────────────────────────┐                │
│  │  MCP Server           │    generates          │   Project Generator       │                │
│  │  (FastMCP)            │◄─────────────────────►│                           │                │
│  │                       │                        │  - create_project()       │                │
│  │  - Tools API          │                        │  - CreateProjectRequest   │                │
│  │  - Resources API      │                        │    handling               │                │
│  │  - Context management │                        │  - Output management      │                │
│  │  - Progress reporting │                        │                           │                │
│  └───────────┬───────────┘                        └───────────────────────────┘                │
│              │                                                                                  │
└──────────────┼──────────────────────────────────────────────────────────────────────────────────┘
               │
               │ communicates via SSE
               ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                      SSE TRANSPORT LAYER                                         │
│                                                                                                  │
│  - Persistent connections                                                                        │
│  - Real-time updates                                                                            │
│  - Progress streaming                                                                           │
│  - Error reporting                                                                              │
│                                                                                                  │
└──────────────┬───────────────────────────────────────────────────────────────────────────────────┘
               │
               │ connects to
               ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                           CLIENTS                                                │
│                                                                                                  │
│  ┌───────────────────────┐    ┌───────────────────────────┐    ┌───────────────────────────┐    │
│  │  LLM Applications     │    │   Web UI Clients          │    │   API Clients             │    │
│  │  (Claude, etc.)       │    │                           │    │                           │    │
│  │                       │    │                           │    │                           │    │
│  └───────────────────────┘    └───────────────────────────┘    └───────────────────────────┘    │
│                                                                                                  │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Template Registry Manager

**Responsibilities**:
- Manages the lifecycle of cookiecutter templates
- Handles template discovery, addition, updating, and removal
- Maintains template metadata

**Key Interfaces**:
- `list_templates() -> List[TemplateInfo]`
- `add_template(url, name, description) -> TemplateInfo`
- `update_template(template_name, force) -> TemplateInfo`
- `remove_template(template_name) -> str`
- `discover_templates() -> List[TemplateInfo]`

**Dependencies**:
- Template Repository
- Virtual Environment Manager

### 2. Template Repository

**Responsibilities**:
- Stores template metadata
- Persists template information between sessions
- Tracks template versions and updates

**Storage Format**:
- JSON files in `templates/` directory
- In-memory cache for fast access

### 3. Virtual Environment Manager

**Responsibilities**:
- Creates isolated Python environments for templates
- Executes commands within specific environments
- Manages environment resources and cleanup

**Key Interfaces**:
- `_create_venv(path) -> None`
- `_run_in_venv(venv_path, cmd) -> str`
- `_cleanup_venv(path) -> None`

**Dependencies**:
- Environment Repository
- Python's venv module

### 4. Environment Repository

**Responsibilities**:
- Stores virtual environments for each template
- Contains cloned template repositories
- Isolates dependencies between templates

**Storage Format**:
- Directory structure in `venvs/` folder
- Each template has its own subdirectory

### 5. Interface Generator

**Responsibilities**:
- Extracts variables from cookiecutter templates
- Determines variable types and defaults
- Generates MCP-compatible interfaces

**Key Interfaces**:
- `_get_template_variables(template_dir) -> List[TemplateVariable]`
- `get_template_variables(template_name) -> List[TemplateVariable]`

**Dependencies**:
- Template Variables Cache
- Virtual Environment Manager

### 6. Template Variables Cache

**Responsibilities**:
- Stores extracted template variables
- Improves performance by avoiding repeated parsing
- Maintains type information and defaults

**Storage Format**:
- In-memory cache
- Serialized in template metadata files

### 7. MCP Server

**Responsibilities**:
- Exposes template functionality through MCP
- Manages client connections and contexts
- Handles progress reporting and errors

**Key Interfaces**:
- MCP Tools API
- MCP Resources API

**Dependencies**:
- FastMCP library
- Template Registry Manager
- Interface Generator
- Project Generator

### 8. Project Generator

**Responsibilities**:
- Creates projects from templates
- Handles variable substitution
- Manages output directories

**Key Interfaces**:
- `create_project(request) -> str`

**Dependencies**:
- Virtual Environment Manager
- Template Registry Manager

### 9. SSE Transport Layer

**Responsibilities**:
- Provides real-time communication with clients
- Streams progress updates and results
- Handles connection management

**Key Features**:
- Persistent connections
- Event streaming
- Web compatibility

### 10. Clients

**Types**:
- LLM-powered applications (Claude)
- Web UI clients
- API clients

**Interactions**:
- Connect to SSE endpoint
- Send requests to MCP server
- Receive real-time updates

## Data Flow Diagrams

### Template Registration Flow

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

### Project Creation Flow

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

## Conclusion

This component diagram illustrates the modular architecture of the dynamo-mcp system. Each component has well-defined responsibilities and interfaces, allowing for independent development and testing. The system's design emphasizes:

1. **Separation of concerns**: Each component has a specific responsibility
2. **Modularity**: Components can be developed and tested independently
3. **Clear interfaces**: Well-defined APIs between components
4. **Extensibility**: New components can be added without major changes

The architecture supports the key requirements of template management, virtual environment isolation, dynamic interface generation, and SSE transport while maintaining a clean, maintainable codebase.