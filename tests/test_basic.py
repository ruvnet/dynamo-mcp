"""
Basic tests for the dynamo-mcp system.
"""
import os
import sys
import asyncio
import unittest
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dynamo_mcp.core.models import TemplateInfo, TemplateVariable, CreateProjectRequest
from dynamo_mcp.core.template_registry import TemplateRegistry
from dynamo_mcp.core.environment_manager import EnvironmentManager
from dynamo_mcp.core.interface_generator import InterfaceGenerator
from dynamo_mcp.core.project_generator import ProjectGenerator


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


class TestTemplateRegistry(unittest.TestCase):
    """Test the template registry."""
    
    def setUp(self):
        """Set up the test environment."""
        self.registry = TemplateRegistry()
        self.ctx = MockContext()
    
    def test_list_templates(self):
        """Test listing templates."""
        templates = asyncio.run(self.registry.list_templates())
        self.assertIsInstance(templates, list)
    
    def test_discover_templates(self):
        """Test discovering templates."""
        templates = asyncio.run(self.registry.discover_templates(self.ctx))
        self.assertIsInstance(templates, list)
        self.assertTrue(len(templates) > 0)
        self.assertIsInstance(templates[0], TemplateInfo)


class TestEnvironmentManager(unittest.TestCase):
    """Test the environment manager."""
    
    def setUp(self):
        """Set up the test environment."""
        self.test_venv_path = Path("test_venv")
    
    def tearDown(self):
        """Clean up the test environment."""
        if self.test_venv_path.exists():
            asyncio.run(EnvironmentManager.cleanup_venv(self.test_venv_path))
    
    def test_create_venv(self):
        """Test creating a virtual environment."""
        # Skip this test if running in CI
        if os.environ.get("CI") == "true":
            self.skipTest("Skipping in CI environment")
        
        EnvironmentManager.create_venv(self.test_venv_path)
        
        # Check if Python executable exists
        python_path = EnvironmentManager._get_python_path(self.test_venv_path)
        self.assertTrue(python_path.exists())


if __name__ == "__main__":
    unittest.main()