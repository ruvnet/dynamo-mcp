"""
Configuration for the dynamo-mcp system.

This module provides configuration variables for the dynamo-mcp system.
"""
import os
from pathlib import Path

# Base directories
# Base directories
BASE_DIR = os.environ.get("DYNAMO_MCP_BASE_DIR", os.path.expanduser("~/.dynamo-mcp"))
TEMPLATES_DIR = os.environ.get("DYNAMO_MCP_TEMPLATES_DIR", os.path.join(BASE_DIR, "templates"))
VENVS_DIR = os.environ.get("DYNAMO_MCP_VENVS_DIR", os.path.join(BASE_DIR, "venvs"))
CONFIG_DIR = os.environ.get("DYNAMO_MCP_CONFIG_DIR", os.path.join(BASE_DIR, "config"))
# For testing, use local directories
if os.environ.get("DYNAMO_MCP_TESTING") == "true":
    TEMPLATES_DIR = "dynamo_mcp/templates"
    VENVS_DIR = "dynamo_mcp/venvs"
    CONFIG_DIR = "dynamo_mcp/config"

# Server configuration
HOST = os.environ.get("DYNAMO_MCP_HOST", "localhost")
PORT = int(os.environ.get("DYNAMO_MCP_PORT", "3000"))
TRANSPORT = os.environ.get("DYNAMO_MCP_TRANSPORT", "sse")

# Authentication
AUTH_ENABLED = os.environ.get("DYNAMO_MCP_AUTH_ENABLED", "false").lower() == "true"
AUTH_USERNAME = os.environ.get("DYNAMO_MCP_AUTH_USERNAME", "admin")
AUTH_PASSWORD = os.environ.get("DYNAMO_MCP_AUTH_PASSWORD", "password")

# Create directories if they don't exist
Path(TEMPLATES_DIR).mkdir(parents=True, exist_ok=True)
Path(VENVS_DIR).mkdir(parents=True, exist_ok=True)
Path(CONFIG_DIR).mkdir(parents=True, exist_ok=True)