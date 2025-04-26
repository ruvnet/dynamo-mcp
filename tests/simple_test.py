"""
Simple test for the dynamo-mcp system.

This script tests if the MCP server is working correctly by directly using the MCPServer class.
"""
import os
import sys
import json
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dynamo_mcp.api.mcp_server import MCPServer
from dynamo_mcp.core.models import TemplateInfo, TemplateVariable, CreateProjectRequest


class MockContext:
    """Mock MCP context for testing."""
    
    async def info(self, message):
        """Log an info message."""
        print(f"INFO: {message}")
    
    async def progress(self, message, percent):
        """Log a progress message."""
        print(f"PROGRESS ({percent}%): {message}")
    
    async def error(self, message):
        """Log an error message."""
        print(f"ERROR: {message}")


async def test_list_templates():
    """Test the list_templates tool."""
    # Create server
    server = MCPServer()
    
    # Create context
    ctx = MockContext()
    
    # Call tool
    templates = await server.template_registry.list_templates()
    
    # Print result
    print(f"Templates: {templates}")
    
    return templates


def main():
    """Run the test."""
    print("Starting test...")
    
    try:
        # Set testing mode
        os.environ["DYNAMO_MCP_TESTING"] = "true"
        
        # Run test
        templates = asyncio.run(test_list_templates())
        
        # Check result
        if templates is not None:
            print("Test passed!")
            return 0
        else:
            print("Test failed: No templates returned")
            return 1
    except Exception as e:
        print(f"Test failed with exception: {e}")
        return 1
    finally:
        print("Test completed")


if __name__ == "__main__":
    exit_code = main()
    print(f"Exiting with code {exit_code}")
    sys.exit(exit_code)