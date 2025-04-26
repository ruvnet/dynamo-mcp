"""
Project Generator for the dynamo-mcp system.

This module provides functionality for generating projects from cookiecutter templates.
"""
import os
import sys
import json
import asyncio
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional

from fastmcp import Context

from dynamo_mcp.core.models import CreateProjectRequest
from dynamo_mcp.core.template_registry import TemplateRegistry
from dynamo_mcp.core.environment_manager import EnvironmentManager
from dynamo_mcp.utils.exceptions import (
    TemplateNotFoundError, ProjectGenerationError
)


class ProjectGenerator:
    """Generator for projects from templates."""
    
    def __init__(self, template_registry: TemplateRegistry):
        """Initialize the project generator.
        
        Args:
            template_registry: The template registry to use
        """
        self.template_registry = template_registry
    
    async def create_project(self, request: CreateProjectRequest, ctx: Context) -> str:
        """Create a project from a cookiecutter template.
        
        Args:
            request: The project creation request
            ctx: MCP context
        
        Returns:
            The path to the generated project
        
        Raises:
            TemplateNotFoundError: If the template is not found
            ProjectGenerationError: If there's an error generating the project
        """
        # Check if template exists
        if request.template_name not in self.template_registry.templates:
            raise TemplateNotFoundError(f"Template '{request.template_name}' not found")
        
        # Get template info
        template_info = self.template_registry.templates[request.template_name]
        
        await ctx.info(f"Generating project from template: {request.template_name}")
        
        # Create output directory if it doesn't exist
        os.makedirs(request.output_dir, exist_ok=True)
        
        # Create temporary config file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(request.variables, f)
            config_file = f.name
        
        try:
            # Run cookiecutter
            await ctx.info(f"Running cookiecutter with template: {template_info.path}")
            
            try:
                # Get Python executable path
                python_path = EnvironmentManager._get_python_path(Path(template_info.venv_path))
                
                # Verify that cookiecutter is installed
                try:
                    check_process = await asyncio.create_subprocess_exec(
                        str(python_path), "-m", "pip", "list",
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    stdout, stderr = await check_process.communicate()
                    
                    if "cookiecutter" not in stdout.decode():
                        await ctx.info(f"Cookiecutter not found in virtual environment, installing...")
                        await EnvironmentManager.install_package(template_info.venv_path, "cookiecutter")
                except Exception as e:
                    await ctx.info(f"Error checking for cookiecutter: {e}, attempting to install...")
                    await EnvironmentManager.install_package(template_info.venv_path, "cookiecutter")
                
                # Run cookiecutter
                process = await asyncio.create_subprocess_exec(
                    str(python_path), "-m", "cookiecutter", template_info.path,
                    "--no-input", "--output-dir", request.output_dir,
                    "--config-file", config_file,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await process.communicate()
                
                # Check if cookiecutter succeeded
                if process.returncode != 0:
                    raise ProjectGenerationError(f"Failed to generate project: {stderr.decode()}")
            except EnvironmentError as e:
                # If there's an issue with the virtual environment, try using the system Python
                await ctx.info(f"Error with virtual environment: {e}, falling back to system Python...")
                
                process = await asyncio.create_subprocess_exec(
                    sys.executable, "-m", "cookiecutter", template_info.path,
                    "--no-input", "--output-dir", request.output_dir,
                    "--config-file", config_file,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await process.communicate()
                
                # Check if cookiecutter succeeded
                if process.returncode != 0:
                    raise ProjectGenerationError(f"Failed to generate project with system Python: {stderr.decode()}")
            
            # Determine project directory
            project_slug = request.variables.get("project_slug")
            if not project_slug:
                # Try to determine project directory from cookiecutter output
                output = stdout.decode()
                for line in output.splitlines():
                    if line.startswith("Created project at "):
                        project_path = line.split("Created project at ")[1]
                        break
                else:
                    # Fall back to output directory
                    project_path = request.output_dir
            else:
                # Use project slug
                project_path = os.path.join(request.output_dir, project_slug)
            
            await ctx.info(f"Project generated successfully: {project_path}")
            
            return project_path
        except Exception as e:
            raise ProjectGenerationError(f"Failed to generate project: {e}")
        finally:
            # Clean up temporary config file
            try:
                os.unlink(config_file)
            except Exception:
                pass