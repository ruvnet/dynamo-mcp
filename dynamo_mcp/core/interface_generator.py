"""
Interface Generator for the dynamo-mcp system.

This module provides functionality for generating interfaces for cookiecutter templates.
"""
import os
import json
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional

from fastmcp import Context

from dynamo_mcp.core.models import TemplateVariable
from dynamo_mcp.core.template_registry import TemplateRegistry
from dynamo_mcp.core.environment_manager import EnvironmentManager
from dynamo_mcp.utils.exceptions import (
    TemplateNotFoundError, InterfaceGenerationError
)


class InterfaceGenerator:
    """Generator for template interfaces."""
    
    def __init__(self, template_registry: TemplateRegistry):
        """Initialize the interface generator.
        
        Args:
            template_registry: The template registry to use
        """
        self.template_registry = template_registry
    
    async def get_template_variables(self, template_name: str, ctx: Context) -> List[TemplateVariable]:
        """Get the variables for a cookiecutter template.
        
        Args:
            template_name: Name of the template
            ctx: MCP context
        
        Returns:
            A list of template variables
        
        Raises:
            TemplateNotFoundError: If the template is not found
            InterfaceGenerationError: If there's an error generating the interface
        """
        # Check if template exists
        if template_name not in self.template_registry.templates:
            raise TemplateNotFoundError(f"Template '{template_name}' not found")
        
        # Get template info
        template_info = self.template_registry.templates[template_name]
        
        await ctx.info(f"Extracting variables from template: {template_name}")
        
        # Get cookiecutter.json path
        cookiecutter_json_path = os.path.join(template_info.path, "cookiecutter.json")
        
        # Check if cookiecutter.json exists
        if not os.path.exists(cookiecutter_json_path):
            raise InterfaceGenerationError(f"cookiecutter.json not found in template: {template_name}")
        
        try:
            # Load cookiecutter.json
            with open(cookiecutter_json_path, "r") as f:
                cookiecutter_json = json.load(f)
            
            # Extract variables
            variables = []
            for key, value in cookiecutter_json.items():
                # Skip private variables (starting with _)
                if key.startswith("_"):
                    continue
                
                # Determine variable type
                var_type = self._get_variable_type(value)
                
                # Determine variable options
                options = self._get_variable_options(value)
                
                # Create variable
                variable = TemplateVariable(
                    name=key,
                    type=var_type,
                    description=self._get_variable_description(key),
                    default=value if var_type != "choice" else options[0] if options else None,
                    options=options
                )
                
                variables.append(variable)
            
            return variables
        except json.JSONDecodeError as e:
            raise InterfaceGenerationError(f"Invalid cookiecutter.json: {e}")
        except Exception as e:
            raise InterfaceGenerationError(f"Failed to extract variables: {e}")
    
    def _get_variable_type(self, value: Any) -> str:
        """Get the type of a variable.
        
        Args:
            value: The variable value
        
        Returns:
            The variable type
        """
        if isinstance(value, str):
            if "{{" in value and "}}" in value:
                return "derived"
            elif value.startswith("y/n") or value.lower() in ["y", "n", "yes", "no"]:
                return "boolean"
            elif "/" in value or "," in value:
                return "choice"
            else:
                return "string"
        elif isinstance(value, bool):
            return "boolean"
        elif isinstance(value, int):
            return "integer"
        elif isinstance(value, float):
            return "float"
        elif isinstance(value, list):
            return "choice"
        elif isinstance(value, dict):
            return "object"
        else:
            return "string"
    
    def _get_variable_options(self, value: Any) -> Optional[List[Any]]:
        """Get the options for a variable.
        
        Args:
            value: The variable value
        
        Returns:
            The variable options, or None if the variable has no options
        """
        if isinstance(value, str):
            if "/" in value:
                return value.split("/")
            elif "," in value:
                return value.split(",")
            elif value.startswith("y/n"):
                return ["y", "n"]
            elif value.lower() in ["y", "n", "yes", "no"]:
                return ["y", "n"]
            else:
                return None
        elif isinstance(value, list):
            return value
        else:
            return None
    
    def _get_variable_description(self, name: str) -> str:
        """Get the description for a variable.
        
        Args:
            name: The variable name
        
        Returns:
            The variable description
        """
        # Common variable descriptions
        descriptions = {
            "project_name": "The name of the project",
            "project_slug": "The slug of the project (used for URLs and file names)",
            "project_short_description": "A short description of the project",
            "full_name": "Your full name",
            "email": "Your email address",
            "github_username": "Your GitHub username",
            "version": "The version of the project",
            "command_line_interface": "The command line interface to use",
            "use_pytest": "Whether to use pytest for testing",
            "use_black": "Whether to use black for code formatting",
            "use_pypi_deployment_with_travis": "Whether to use PyPI deployment with Travis",
            "add_pyup_badge": "Whether to add a PyUp badge",
            "create_author_file": "Whether to create an authors file",
            "open_source_license": "The open source license to use"
        }
        
        # Return description if available, otherwise generate one
        return descriptions.get(name, f"The {name.replace('_', ' ')}")