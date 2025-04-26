"""
MCP Server for the dynamo-mcp system.

This module exposes template functionality through the Model Context Protocol.
"""
import sys
import logging
from typing import List, Dict, Any, Optional
from fastmcp import FastMCP, Context

from dynamo_mcp.core.models import TemplateInfo, TemplateVariable, CreateProjectRequest
from dynamo_mcp.core.template_registry import TemplateRegistry
from dynamo_mcp.core.interface_generator import InterfaceGenerator
from dynamo_mcp.core.project_generator import ProjectGenerator
from dynamo_mcp.utils.config import AUTH_ENABLED, AUTH_USERNAME, AUTH_PASSWORD
from dynamo_mcp.utils.exceptions import TemplateNotFoundError, DynamoMCPError

# Set up logging
logger = logging.getLogger(__name__)


class MCPServer:
    """MCP server for cookiecutter templates."""
    
    def __init__(self):
        """Initialize the MCP server."""
        try:
            # Create core components
            self.template_registry = TemplateRegistry()
            self.interface_generator = InterfaceGenerator(self.template_registry)
            self.project_generator = ProjectGenerator(self.template_registry)
            
            # Create FastMCP server
            self.mcp = FastMCP("Cookiecutter Templates", dependencies=["cookiecutter"])
            
            # Register tools
            self.register_tools()
            
            # Register resources
            self.register_resources()
            
            # Configure authentication if enabled
            if AUTH_ENABLED:
                from fastmcp.security import BasicAuthMiddleware
                self.mcp.add_middleware(BasicAuthMiddleware(
                    username=AUTH_USERNAME,
                    password=AUTH_PASSWORD
                ))
                
                logger.info("Authentication enabled")
        except Exception as e:
            logger.error(f"Failed to initialize MCP server: {e}", exc_info=True)
            sys.exit(1)
    
    def register_tools(self):
        """Register MCP tools."""
        # Template Management Tools
        @self.mcp.tool()
        async def list_templates(ctx: Context) -> List[TemplateInfo]:
            """List all available cookiecutter templates."""
            try:
                return await self.template_registry.list_templates()
            except Exception as e:
                logger.error(f"Error listing templates: {e}", exc_info=True)
                raise
        
        @self.mcp.tool()
        async def add_template(url: str, ctx: Context, name: Optional[str] = None, 
                              description: Optional[str] = None) -> TemplateInfo:
            """Add a new cookiecutter template and create a virtual environment for it.
            
            Args:
                url: URL of the cookiecutter template repository
                name: Name for the template (derived from URL if not provided)
                description: Description of the template
            """
            try:
                return await self.template_registry.add_template(url, ctx, name, description)
            except Exception as e:
                logger.error(f"Error adding template: {e}", exc_info=True)
                raise
        
        @self.mcp.tool()
        async def update_template(template_name: str, ctx: Context, force: bool = False) -> TemplateInfo:
            """Update a cookiecutter template to the latest version.
            
            Args:
                template_name: Name of the template to update
                force: Whether to force update even if not needed
            """
            try:
                return await self.template_registry.update_template(template_name, ctx, force)
            except Exception as e:
                logger.error(f"Error updating template: {e}", exc_info=True)
                raise
        
        @self.mcp.tool()
        async def remove_template(template_name: str, ctx: Context) -> str:
            """Remove a cookiecutter template and its virtual environment.
            
            Args:
                template_name: Name of the template to remove
            """
            try:
                return await self.template_registry.remove_template(template_name, ctx)
            except Exception as e:
                logger.error(f"Error removing template: {e}", exc_info=True)
                raise
        
        @self.mcp.tool()
        async def discover_templates(ctx: Context) -> List[TemplateInfo]:
            """Discover popular cookiecutter templates from GitHub."""
            try:
                return await self.template_registry.discover_templates(ctx)
            except Exception as e:
                logger.error(f"Error discovering templates: {e}", exc_info=True)
                raise
        
        # Template Variables Tools
        @self.mcp.tool()
        async def get_template_variables(template_name: str, ctx: Context) -> List[TemplateVariable]:
            """Get the variables for a cookiecutter template.
            
            Args:
                template_name: Name of the template
            """
            try:
                return await self.interface_generator.get_template_variables(template_name, ctx)
            except Exception as e:
                logger.error(f"Error getting template variables: {e}", exc_info=True)
                raise
        
        # Project Generation Tools
        @self.mcp.tool()
        async def create_project(request: Dict[str, Any], ctx: Context) -> str:
            """Create a project from a cookiecutter template.
            
            Args:
                request: Project creation request with template_name, output_dir, and variables
            """
            try:
                # Handle both direct request and nested request
                if "request" in request:
                    request = request["request"]
                
                # Convert dictionary to CreateProjectRequest
                project_request = CreateProjectRequest(
                    template_name=request["template_name"],
                    output_dir=request["output_dir"],
                    variables=request["variables"]
                )
                
                return await self.project_generator.create_project(project_request, ctx)
            except Exception as e:
                logger.error(f"Error creating project: {e}", exc_info=True)
                raise
    
    def register_resources(self):
        """Register MCP resources."""
        # Template Listing Resource
        @self.mcp.resource("templates://list")
        async def get_templates_resource(ctx: Context) -> List[TemplateInfo]:
            """Get a list of all available cookiecutter templates."""
            try:
                return await self.template_registry.list_templates()
            except Exception as e:
                logger.error(f"Error accessing templates list resource: {e}", exc_info=True)
                raise
        
        # Template Variables Resource
        @self.mcp.resource("templates://{name}/variables")
        async def get_template_variables_resource(name: str, ctx: Context) -> List[TemplateVariable]:
            """Get the variables for a specific cookiecutter template."""
            try:
                return await self.interface_generator.get_template_variables(name, ctx)
            except Exception as e:
                logger.error(f"Error accessing template variables resource: {e}", exc_info=True)
                raise
        
        # Template Information Resource
        @self.mcp.resource("templates://{name}/info")
        async def get_template_info_resource(name: str, ctx: Context) -> TemplateInfo:
            """Get information about a specific cookiecutter template."""
            try:
                templates = self.template_registry.templates
                if name not in templates:
                    raise TemplateNotFoundError(f"Template '{name}' not found")
                return templates[name]
            except Exception as e:
                logger.error(f"Error accessing template info resource: {e}", exc_info=True)
                raise
    
    def run(self, transport: str = "sse", host: str = "localhost", port: int = 8000):
        """Run the MCP server.
        
        Args:
            transport: Transport type ("sse" or "stdio")
            host: Host to bind to
            port: Port to bind to
        """
        try:
            logger.info(f"Starting MCP server with {transport} transport")
            
            if transport == "stdio":
                # For stdio transport, don't pass host and port
                self.mcp.run(transport=transport)
            else:
                # For other transports like SSE, pass host and port
                self.mcp.run(transport=transport, host=host, port=port)
        except KeyboardInterrupt:
            logger.info("MCP server stopped by user")
            sys.exit(0)
        except Exception as e:
            logger.error(f"Error running MCP server: {e}", exc_info=True)
            sys.exit(1)