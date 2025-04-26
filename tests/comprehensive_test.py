"""
Comprehensive test for the dynamo-mcp system.

This script tests all the MCP tools by directly using the MCPServer class.
"""
import os
import sys
import json
import asyncio
import shutil
import uuid
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


async def test_list_templates(server, ctx):
    """Test the list_templates tool."""
    print("\n=== Testing list_templates ===")
    templates = await server.template_registry.list_templates()
    print(f"Templates: {templates}")
    return templates


async def test_discover_templates(server, ctx):
    """Test the discover_templates tool."""
    print("\n=== Testing discover_templates ===")
    templates = await server.template_registry.discover_templates(ctx)
    print(f"Discovered templates: {len(templates)}")
    return templates


async def test_add_template(server, ctx, template_name):
    """Test the add_template tool."""
    print(f"\n=== Testing add_template ({template_name}) ===")
    
    # First check if template already exists and remove it
    templates = await server.template_registry.list_templates()
    for template in templates:
        if template.name == template_name:
            print(f"Template {template_name} already exists, removing it first")
            await server.template_registry.remove_template(template_name, ctx)
    
    # Now add the template
    template = await server.template_registry.add_template(
        "https://github.com/audreyfeldroy/cookiecutter-pypackage.git",
        ctx,
        template_name,
        "Test template"
    )
    print(f"Added template: {template}")
    return template


async def test_get_template_variables(server, ctx, template_name):
    """Test the get_template_variables tool."""
    print(f"\n=== Testing get_template_variables for {template_name} ===")
    variables = await server.interface_generator.get_template_variables(template_name, ctx)
    print(f"Template variables: {len(variables)}")
    return variables


async def test_update_template(server, ctx, template_name):
    """Test the update_template tool."""
    print(f"\n=== Testing update_template for {template_name} ===")
    template = await server.template_registry.update_template(template_name, ctx, True)
    print(f"Updated template: {template}")
    return template


async def test_create_project(server, ctx, template_name):
    """Test the create_project tool."""
    print(f"\n=== Testing create_project for {template_name} ===")
    
    # Create temporary output directory
    output_dir = Path("test_output")
    output_dir.mkdir(exist_ok=True)
    
    # Create project request
    request = CreateProjectRequest(
        template_name=template_name,
        output_dir=str(output_dir),
        variables={
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
    )
    
    # Create project
    project_path = await server.project_generator.create_project(request, ctx)
    print(f"Created project at: {project_path}")
    
    # Clean up
    if output_dir.exists():
        shutil.rmtree(output_dir)
    
    return project_path


async def test_remove_template(server, ctx, template_name):
    """Test the remove_template tool."""
    print(f"\n=== Testing remove_template for {template_name} ===")
    result = await server.template_registry.remove_template(template_name, ctx)
    print(f"Removed template: {result}")
    return result


async def run_tests():
    """Run all tests."""
    # Create server
    server = MCPServer()
    
    # Create context
    ctx = MockContext()
    
    # Generate a unique template name for this test run
    template_name = f"test-template-{uuid.uuid4().hex[:8]}"
    print(f"Using unique template name: {template_name}")
    
    # Test list_templates
    templates = await test_list_templates(server, ctx)
    
    # Test discover_templates
    discovered_templates = await test_discover_templates(server, ctx)
    
    # Test add_template
    template = await test_add_template(server, ctx, template_name)
    
    # Test get_template_variables
    variables = await test_get_template_variables(server, ctx, template.name)
    
    # Test update_template
    updated_template = await test_update_template(server, ctx, template.name)
    
    # Test create_project
    project_path = await test_create_project(server, ctx, template.name)
    
    # Test remove_template
    result = await test_remove_template(server, ctx, template.name)
    
    # Final list_templates to verify template was removed
    final_templates = await test_list_templates(server, ctx)
    
    return True


def main():
    """Run the test."""
    print("Starting comprehensive test...")
    
    try:
        # Set testing mode
        os.environ["DYNAMO_MCP_TESTING"] = "true"
        
        # Run tests
        success = asyncio.run(run_tests())
        
        # Check result
        if success:
            print("\nAll tests passed!")
            return 0
        else:
            print("\nSome tests failed")
            return 1
    except Exception as e:
        print(f"\nTests failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        print("\nTests completed")


if __name__ == "__main__":
    exit_code = main()
    print(f"Exiting with code {exit_code}")
    sys.exit(exit_code)