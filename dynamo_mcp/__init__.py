"""
Dynamo MCP - A dynamic MCP registry for cookiecutter templates.

This package provides functionality for discovering, registering, and managing
cookiecutter templates through the Model Context Protocol (MCP).
"""
__version__ = "0.1.0"

from dynamo_mcp.core.template_registry import TemplateRegistry
from dynamo_mcp.core.environment_manager import EnvironmentManager
from dynamo_mcp.core.interface_generator import InterfaceGenerator
from dynamo_mcp.core.project_generator import ProjectGenerator
from dynamo_mcp.api.mcp_server import MCPServer