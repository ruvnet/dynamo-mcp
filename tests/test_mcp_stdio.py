"""
Tests for the MCP server with stdio transport.

This module tests the MCP server with stdio transport by sending MCP requests
and verifying the responses.
"""
import os
import sys
import json
import asyncio
import unittest
import subprocess
import signal
import time
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dynamo_mcp.core.models import TemplateInfo, TemplateVariable, CreateProjectRequest


class MCPStdioClient:
    """Client for communicating with an MCP server over stdio."""
    
    def __init__(self, server_process: subprocess.Popen):
        """Initialize the client.
        
        Args:
            server_process: The server process to communicate with
        """
        self.server_process = server_process
        self.request_id = 0
    
    async def call_tool(self, tool_name: str, params: Dict[str, Any] = None, timeout: int = 10) -> Any:
        """Call an MCP tool.
        
        Args:
            tool_name: The name of the tool to call
            params: The parameters to pass to the tool
            timeout: Timeout in seconds
        
        Returns:
            The tool result
        
        Raises:
            TimeoutError: If the request times out
            Exception: If there's an error calling the tool
        """
        # Increment request ID
        self.request_id += 1
        
        # Create request
        request = {
            "jsonrpc": "2.0",
            "method": "mcp.call_tool",
            "params": {
                "tool": tool_name,
                "arguments": params or {}
            },
            "id": self.request_id
        }
        
        # Send request
        request_json = json.dumps(request) + "\n"
        self.server_process.stdin.write(request_json.encode())
        self.server_process.stdin.flush()
        
        # Read response with timeout
        try:
            response_line = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(
                    None, self.server_process.stdout.readline
                ),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            raise TimeoutError(f"Timeout waiting for response from tool {tool_name}")
        
        # Check if process is still alive
        if self.server_process.poll() is not None:
            raise Exception(f"Server process exited with code {self.server_process.returncode}")
        
        # Parse response
        try:
            response = json.loads(response_line.decode())
        except json.JSONDecodeError:
            raise Exception(f"Invalid JSON response: {response_line.decode()}")
        
        # Check for errors
        if "error" in response:
            raise Exception(f"Error calling tool {tool_name}: {response['error']}")
        
        # Return result
        return response["result"]
    
    async def access_resource(self, uri: str, timeout: int = 10) -> Any:
        """Access an MCP resource.
        
        Args:
            uri: The URI of the resource to access
            timeout: Timeout in seconds
        
        Returns:
            The resource content
        
        Raises:
            TimeoutError: If the request times out
            Exception: If there's an error accessing the resource
        """
        # Increment request ID
        self.request_id += 1
        
        # Create request
        request = {
            "jsonrpc": "2.0",
            "method": "mcp.access_resource",
            "params": {
                "uri": uri
            },
            "id": self.request_id
        }
        
        # Send request
        request_json = json.dumps(request) + "\n"
        self.server_process.stdin.write(request_json.encode())
        self.server_process.stdin.flush()
        
        # Read response with timeout
        try:
            response_line = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(
                    None, self.server_process.stdout.readline
                ),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            raise TimeoutError(f"Timeout waiting for response from resource {uri}")
        
        # Check if process is still alive
        if self.server_process.poll() is not None:
            raise Exception(f"Server process exited with code {self.server_process.returncode}")
        
        # Parse response
        try:
            response = json.loads(response_line.decode())
        except json.JSONDecodeError:
            raise Exception(f"Invalid JSON response: {response_line.decode()}")
        
        # Check for errors
        if "error" in response:
            raise Exception(f"Error accessing resource {uri}: {response['error']}")
        
        # Return result
        return response["result"]


class TestMCPStdio(unittest.TestCase):
    """Test the MCP server with stdio transport."""
    
    @classmethod
    def setUpClass(cls):
        """Set up the test environment."""
        # Start MCP server with timeout
        try:
            cls.server_process = subprocess.Popen(
                [sys.executable, "-m", "dynamo_mcp.main", "--transport", "stdio", "--testing"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=1,
                universal_newlines=False,
                start_new_session=True  # Create a new process group
            )
            
            # Create client
            cls.client = MCPStdioClient(cls.server_process)
            
            # Wait for server to start (with timeout)
            start_time = time.time()
            max_wait_time = 5  # 5 seconds
            
            while time.time() - start_time < max_wait_time:
                # Check if process is still running
                if cls.server_process.poll() is not None:
                    stderr = cls.server_process.stderr.read().decode()
                    raise Exception(f"Server process exited with code {cls.server_process.returncode}: {stderr}")
                
                # Wait a bit
                time.sleep(0.1)
                
                # Try to ping the server
                try:
                    # Just wait a bit for the server to start
                    time.sleep(1)
                    break
                except Exception:
                    continue
            
            # Check if we timed out
            if time.time() - start_time >= max_wait_time:
                cls.tearDownClass()
                raise TimeoutError("Timeout waiting for server to start")
            
        except Exception as e:
            # Clean up if setup fails
            if hasattr(cls, 'server_process') and cls.server_process:
                cls._terminate_process(cls.server_process)
            raise Exception(f"Failed to set up test environment: {e}")
    
    @classmethod
    def tearDownClass(cls):
        """Clean up the test environment."""
        # Terminate server
        if hasattr(cls, 'server_process') and cls.server_process:
            cls._terminate_process(cls.server_process)
    
    @classmethod
    def _terminate_process(cls, process):
        """Terminate a process and all its children."""
        try:
            # Try to terminate gracefully
            if process.poll() is None:
                # Send SIGTERM to process group
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                
                # Wait for process to terminate
                for _ in range(10):  # Wait up to 1 second
                    if process.poll() is not None:
                        break
                    time.sleep(0.1)
                
                # If process is still running, kill it
                if process.poll() is None:
                    os.killpg(os.getpgid(process.pid), signal.SIGKILL)
        except Exception as e:
            print(f"Error terminating process: {e}")
    
    def setUp(self):
        """Set up the test."""
        # Skip all tests if server is not running
        if not hasattr(self, 'server_process') or self.server_process.poll() is not None:
            self.skipTest("Server is not running")
    
    def test_list_templates(self):
        """Test the list_templates tool."""
        try:
            # Call tool
            templates = asyncio.run(self.client.call_tool("list_templates"))
            
            # Verify response
            self.assertIsInstance(templates, list)
            
            # If python-package template exists, verify its properties
            python_package = next((t for t in templates if t["name"] == "python-package"), None)
            if python_package:
                self.assertEqual(python_package["name"], "python-package")
                self.assertIn("url", python_package)
                self.assertIn("path", python_package)
                self.assertIn("venv_path", python_package)
        except Exception as e:
            self.fail(f"Test failed: {e}")
    
    def test_discover_templates(self):
        """Test the discover_templates tool."""
        try:
            # Call tool
            templates = asyncio.run(self.client.call_tool("discover_templates"))
            
            # Verify response
            self.assertIsInstance(templates, list)
            self.assertTrue(len(templates) > 0)
            
            # Verify template properties
            template = templates[0]
            self.assertIn("name", template)
            self.assertIn("url", template)
            self.assertIn("description", template)
        except Exception as e:
            self.fail(f"Test failed: {e}")
    
    def test_get_template_variables(self):
        """Test the get_template_variables tool."""
        try:
            # Skip if python-package template doesn't exist
            templates = asyncio.run(self.client.call_tool("list_templates"))
            python_package = next((t for t in templates if t["name"] == "python-package"), None)
            if not python_package:
                self.skipTest("python-package template not found")
            
            # Call tool
            variables = asyncio.run(self.client.call_tool("get_template_variables", {
                "template_name": "python-package"
            }))
            
            # Verify response
            self.assertIsInstance(variables, list)
            self.assertTrue(len(variables) > 0)
            
            # Verify variable properties
            variable = variables[0]
            self.assertIn("name", variable)
            self.assertIn("type", variable)
            self.assertIn("description", variable)
        except Exception as e:
            self.fail(f"Test failed: {e}")
    
    def test_add_template(self):
        """Test the add_template tool."""
        try:
            # Skip if test-template already exists
            templates = asyncio.run(self.client.call_tool("list_templates"))
            test_template = next((t for t in templates if t["name"] == "test-template"), None)
            if test_template:
                self.skipTest("test-template already exists")
            
            # Call tool
            template = asyncio.run(self.client.call_tool("add_template", {
                "url": "https://github.com/audreyfeldroy/cookiecutter-pypackage.git",
                "name": "test-template",
                "description": "Test template"
            }, timeout=30))  # Longer timeout for git clone
            
            # Verify response
            self.assertIsInstance(template, dict)
            self.assertEqual(template["name"], "test-template")
            self.assertEqual(template["description"], "Test template")
            self.assertIn("path", template)
            self.assertIn("venv_path", template)
        except Exception as e:
            self.fail(f"Test failed: {e}")
        finally:
            # Clean up
            try:
                asyncio.run(self.client.call_tool("remove_template", {
                    "template_name": "test-template"
                }))
            except Exception:
                pass
    
    def test_update_template(self):
        """Test the update_template tool."""
        try:
            # Skip if python-package template doesn't exist
            templates = asyncio.run(self.client.call_tool("list_templates"))
            python_package = next((t for t in templates if t["name"] == "python-package"), None)
            if not python_package:
                self.skipTest("python-package template not found")
            
            # Call tool
            template = asyncio.run(self.client.call_tool("update_template", {
                "template_name": "python-package",
                "force": True
            }, timeout=30))  # Longer timeout for git pull
            
            # Verify response
            self.assertIsInstance(template, dict)
            self.assertEqual(template["name"], "python-package")
            self.assertIn("path", template)
            self.assertIn("venv_path", template)
        except Exception as e:
            self.fail(f"Test failed: {e}")
    
    def test_remove_template(self):
        """Test the remove_template tool."""
        try:
            # Skip if test-template-remove doesn't exist
            templates = asyncio.run(self.client.call_tool("list_templates"))
            test_template = next((t for t in templates if t["name"] == "test-template-remove"), None)
            if not test_template:
                # Add template
                asyncio.run(self.client.call_tool("add_template", {
                    "url": "https://github.com/audreyfeldroy/cookiecutter-pypackage.git",
                    "name": "test-template-remove",
                    "description": "Test template for removal"
                }, timeout=30))  # Longer timeout for git clone
            
            # Call tool
            result = asyncio.run(self.client.call_tool("remove_template", {
                "template_name": "test-template-remove"
            }))
            
            # Verify response
            self.assertIsInstance(result, str)
            self.assertIn("removed successfully", result)
            
            # Verify template is removed
            templates = asyncio.run(self.client.call_tool("list_templates"))
            test_template = next((t for t in templates if t["name"] == "test-template-remove"), None)
            self.assertIsNone(test_template)
        except Exception as e:
            self.fail(f"Test failed: {e}")
    
    def test_create_project(self):
        """Test the create_project tool."""
        try:
            # Skip if python-package template doesn't exist
            templates = asyncio.run(self.client.call_tool("list_templates"))
            python_package = next((t for t in templates if t["name"] == "python-package"), None)
            if not python_package:
                self.skipTest("python-package template not found")
            
            # Create temporary output directory
            output_dir = Path("test_output")
            output_dir.mkdir(exist_ok=True)
            
            # Call tool
            project_path = asyncio.run(self.client.call_tool("create_project", {
                "request": {
                    "template_name": "python-package",
                    "output_dir": str(output_dir),
                    "variables": {
                        "project_name": "Test Project",
                        "project_slug": "test_project",
                        "project_short_description": "Test project description",
                        "full_name": "Test User",
                        "email": "test@example.com",
                        "github_username": "testuser",
                        "version": "0.1.0",
                        "command_line_interface": "Click",
                        "use_pytest": "y",
                        "use_black": "y",
                        "use_pypi_deployment_with_travis": "y",
                        "add_pyup_badge": "y",
                        "create_author_file": "y",
                        "open_source_license": "MIT"
                    }
                }
            }, timeout=30))  # Longer timeout for project creation
            
            # Verify response
            self.assertIsInstance(project_path, str)
            
            # Verify project was created
            project_dir = Path(project_path)
            self.assertTrue(project_dir.exists())
            self.assertTrue(project_dir.is_dir())
            
            # Verify project files
            self.assertTrue(project_dir.joinpath("README.rst").exists())
            self.assertTrue(project_dir.joinpath("setup.py").exists())
        except Exception as e:
            self.fail(f"Test failed: {e}")
        finally:
            # Clean up
            import shutil
            if output_dir.exists():
                shutil.rmtree(output_dir)
    
    def test_templates_list_resource(self):
        """Test the templates://list resource."""
        try:
            # Access resource
            templates = asyncio.run(self.client.access_resource("templates://list"))
            
            # Verify response
            self.assertIsInstance(templates, list)
            
            # If python-package template exists, verify its properties
            python_package = next((t for t in templates if t["name"] == "python-package"), None)
            if python_package:
                self.assertEqual(python_package["name"], "python-package")
                self.assertIn("url", python_package)
                self.assertIn("path", python_package)
                self.assertIn("venv_path", python_package)
        except Exception as e:
            self.fail(f"Test failed: {e}")
    
    def test_template_variables_resource(self):
        """Test the templates://{name}/variables resource."""
        try:
            # Skip if python-package template doesn't exist
            templates = asyncio.run(self.client.call_tool("list_templates"))
            python_package = next((t for t in templates if t["name"] == "python-package"), None)
            if not python_package:
                self.skipTest("python-package template not found")
            
            # Access resource
            variables = asyncio.run(self.client.access_resource("templates://python-package/variables"))
            
            # Verify response
            self.assertIsInstance(variables, list)
            self.assertTrue(len(variables) > 0)
            
            # Verify variable properties
            variable = variables[0]
            self.assertIn("name", variable)
            self.assertIn("type", variable)
            self.assertIn("description", variable)
        except Exception as e:
            self.fail(f"Test failed: {e}")
    
    def test_template_info_resource(self):
        """Test the templates://{name}/info resource."""
        try:
            # Skip if python-package template doesn't exist
            templates = asyncio.run(self.client.call_tool("list_templates"))
            python_package = next((t for t in templates if t["name"] == "python-package"), None)
            if not python_package:
                self.skipTest("python-package template not found")
            
            # Access resource
            template = asyncio.run(self.client.access_resource("templates://python-package/info"))
            
            # Verify response
            self.assertIsInstance(template, dict)
            self.assertEqual(template["name"], "python-package")
            self.assertIn("url", template)
            self.assertIn("path", template)
            self.assertIn("venv_path", template)
        except Exception as e:
            self.fail(f"Test failed: {e}")


if __name__ == "__main__":
    unittest.main(exit=True)  # Ensure exit on completion