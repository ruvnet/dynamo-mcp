"""
Template Registry for the dynamo-mcp system.

This module provides functionality for discovering, registering, and managing
cookiecutter templates.
"""
import os
import re
import json
import asyncio
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

from fastmcp import Context

from dynamo_mcp.core.models import TemplateInfo
from dynamo_mcp.core.environment_manager import EnvironmentManager
from dynamo_mcp.utils.config import TEMPLATES_DIR, VENVS_DIR
from dynamo_mcp.utils.exceptions import (
    TemplateNotFoundError, TemplateExistsError, EnvironmentError
)
from dynamo_mcp.utils.database import (
    ensure_db_exists, get_template_by_name, get_templates_by_category,
    add_template as db_add_template, update_template as db_update_template,
    delete_template, get_all_categories, search_templates,
    convert_db_template_to_model
)


class TemplateRegistry:
    """Registry for cookiecutter templates."""
    
    def __init__(self):
        """Initialize the template registry."""
        self.templates: Dict[str, TemplateInfo] = {}
        self.db_templates: Dict[str, TemplateInfo] = {}
        
        # Ensure database exists
        ensure_db_exists()
        
        # Load templates
        self._load_templates()
    
    def _load_templates(self):
        """Load templates from the templates directory and database."""
        # Create templates directory if it doesn't exist
        Path(TEMPLATES_DIR).mkdir(parents=True, exist_ok=True)
        
        # Create venvs directory if it doesn't exist
        Path(VENVS_DIR).mkdir(parents=True, exist_ok=True)
        
        # Load installed templates from filesystem
        for template_dir in Path(TEMPLATES_DIR).iterdir():
            if not template_dir.is_dir():
                continue
            
            # Get template name
            template_name = template_dir.name
            
            # Get template URL from .git/config
            git_config_path = template_dir / ".git" / "config"
            if not git_config_path.exists():
                continue
            
            # Parse git config to get URL
            url = None
            with open(git_config_path, "r") as f:
                for line in f:
                    if line.strip().startswith("url = "):
                        url = line.strip().split("url = ")[1]
                        break
            
            if not url:
                continue
            
            # Get template description from cookiecutter.json
            description = ""
            category = ""
            tags = []
            
            cookiecutter_json_path = template_dir / "cookiecutter.json"
            if cookiecutter_json_path.exists():
                try:
                    with open(cookiecutter_json_path, "r") as f:
                        cookiecutter_json = json.load(f)
                        if "_description" in cookiecutter_json:
                            description = cookiecutter_json["_description"]
                        if "_category" in cookiecutter_json:
                            category = cookiecutter_json["_category"]
                        if "_tags" in cookiecutter_json:
                            tags = cookiecutter_json["_tags"]
                except json.JSONDecodeError:
                    pass
            
            # Check if template exists in database
            db_template = get_template_by_name(template_name)
            if db_template:
                # Use database values for description, category, and tags if available
                description = db_template["description"] or description
                category = db_template["category"] or category
                tags = db_template["tags"].split(",") if db_template["tags"] else tags
            
            # Create template info
            template_info = TemplateInfo(
                name=template_name,
                url=url,
                description=description,
                path=str(template_dir),
                venv_path=os.path.join(VENVS_DIR, template_name),
                category=category,
                tags=tags
            )
            
            # Add template to registry
            self.templates[template_name] = template_info
            
            # Update database with filesystem template info
            if not db_template:
                db_add_template(
                    name=template_name,
                    url=url,
                    description=description,
                    category=category,
                    tags=",".join(tags) if tags else ""
                )
        
        # Load templates from database that aren't installed
        db_templates = get_templates_by_category()
        for db_template in db_templates:
            template_name = db_template["name"]
            if template_name not in self.templates:
                # Convert database template to model
                template_info = convert_db_template_to_model(db_template)
                # Add to db_templates dictionary
                self.db_templates[template_name] = template_info
    
    async def list_templates(self) -> List[TemplateInfo]:
        """List all available cookiecutter templates.
        
        Returns:
            A list of template info objects
        """
        # Combine installed templates and database templates
        all_templates = list(self.templates.values()) + list(self.db_templates.values())
        return all_templates
    
    async def list_templates_by_category(self, category: Optional[str] = None) -> List[TemplateInfo]:
        """List templates filtered by category.
        
        Args:
            category: Category to filter by, or None for all templates
            
        Returns:
            A list of template info objects
        """
        all_templates = await self.list_templates()
        
        if category:
            return [t for t in all_templates if t.category == category]
        return all_templates
    
    async def get_categories(self) -> List[str]:
        """Get all unique categories.
        
        Returns:
            A list of category names
        """
        return get_all_categories()
    
    async def search_templates(self, query: str) -> List[TemplateInfo]:
        """Search templates by name, description, category, or tags.
        
        Args:
            query: Search query
            
        Returns:
            A list of template info objects
        """
        db_results = search_templates(query)
        results = []
        
        for db_template in db_results:
            template_name = db_template["name"]
            if template_name in self.templates:
                results.append(self.templates[template_name])
            elif template_name in self.db_templates:
                results.append(self.db_templates[template_name])
            else:
                results.append(convert_db_template_to_model(db_template))
        
        return results
    
    async def add_template(self, url: str, ctx: Context, name: Optional[str] = None,
                          description: Optional[str] = None, category: Optional[str] = None,
                          tags: Optional[List[str]] = None) -> TemplateInfo:
        """Add a new cookiecutter template and create a virtual environment for it.
        
        Args:
            url: URL of the cookiecutter template repository
            ctx: MCP context
            name: Name for the template (derived from URL if not provided)
            description: Description of the template
            category: Category of the template
            tags: Tags for the template
        
        Returns:
            The template info object
        
        Raises:
            TemplateExistsError: If the template already exists
            EnvironmentError: If there's an error creating the virtual environment
        """
        # Derive name from URL if not provided
        if not name:
            name = url.split("/")[-1]
            if name.endswith(".git"):
                name = name[:-4]
            if name.startswith("cookiecutter-"):
                name = name[len("cookiecutter-"):]
        
        # Check if template already exists
        if name in self.templates or name in self.db_templates:
            raise TemplateExistsError(f"Template '{name}' already exists")
        
        # Create template directory
        template_dir = os.path.join(TEMPLATES_DIR, name)
        os.makedirs(template_dir, exist_ok=True)
        
        # Clone template repository
        await ctx.info(f"Cloning template repository: {url}")
        try:
            process = await asyncio.create_subprocess_exec(
                "git", "clone", url, template_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                raise EnvironmentError(f"Failed to clone template repository: {stderr.decode()}")
        except Exception as e:
            raise EnvironmentError(f"Failed to clone template repository: {e}")
        
        # Create virtual environment
        venv_path = os.path.join(VENVS_DIR, name)
        await ctx.info(f"Creating virtual environment for template: {name}")
        try:
            EnvironmentManager.create_venv(venv_path)
        except Exception as e:
            raise EnvironmentError(f"Failed to create virtual environment: {e}")
        
        # Install dependencies
        await ctx.info(f"Installing dependencies for template: {name}")
        try:
            # Install cookiecutter in the virtual environment
            await EnvironmentManager.install_package(venv_path, "cookiecutter")
            await ctx.info(f"Cookiecutter installed successfully in virtual environment: {venv_path}")
        except Exception as e:
            raise EnvironmentError(f"Failed to install dependencies: {e}")
        
        # Get template description from cookiecutter.json if not provided
        if not description:
            cookiecutter_json_path = os.path.join(template_dir, "cookiecutter.json")
            if os.path.exists(cookiecutter_json_path):
                try:
                    with open(cookiecutter_json_path, "r") as f:
                        cookiecutter_json = json.load(f)
                        if "_description" in cookiecutter_json:
                            description = cookiecutter_json["_description"]
                        if not category and "_category" in cookiecutter_json:
                            category = cookiecutter_json["_category"]
                        if not tags and "_tags" in cookiecutter_json:
                            tags = cookiecutter_json["_tags"]
                except json.JSONDecodeError:
                    pass
        
        # Create template info
        template_info = TemplateInfo(
            name=name,
            url=url,
            description=description or "",
            path=template_dir,
            venv_path=venv_path,
            category=category or "",
            tags=tags or []
        )
        
        # Add template to registry
        self.templates[name] = template_info
        
        # Add template to database
        db_add_template(
            name=name,
            url=url,
            description=description or "",
            category=category or "",
            tags=",".join(tags) if tags else ""
        )
        
        return template_info
    
    async def update_template(self, template_name: str, ctx: Context, force: bool = False) -> TemplateInfo:
        """Update a cookiecutter template to the latest version.
        
        Args:
            template_name: Name of the template to update
            ctx: MCP context
            force: Whether to force update even if not needed
        
        Returns:
            The template info object
        
        Raises:
            TemplateNotFoundError: If the template is not found
            EnvironmentError: If there's an error updating the template
        """
        # Check if template exists
        if template_name not in self.templates:
            # Check if it exists in database but not installed
            if template_name in self.db_templates:
                # Install the template first
                db_template = get_template_by_name(template_name)
                if db_template:
                    await self.add_template(
                        url=db_template["url"],
                        ctx=ctx,
                        name=template_name,
                        description=db_template["description"],
                        category=db_template["category"],
                        tags=db_template["tags"].split(",") if db_template["tags"] else []
                    )
                else:
                    raise TemplateNotFoundError(f"Template '{template_name}' not found")
            else:
                raise TemplateNotFoundError(f"Template '{template_name}' not found")
        
        # Get template info
        template_info = self.templates[template_name]
        
        # Update template
        await ctx.info(f"Updating template: {template_name}")
        try:
            process = await asyncio.create_subprocess_exec(
                "git", "-C", template_info.path, "pull",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                raise EnvironmentError(f"Failed to update template: {stderr.decode()}")
            
            # Check if update was needed
            if not force and "Already up to date." in stdout.decode():
                await ctx.info(f"Template '{template_name}' is already up to date")
            else:
                await ctx.info(f"Template '{template_name}' updated successfully")
                
                # Update database entry
                db_update_template(
                    template_name,
                    url=template_info.url,
                    description=template_info.description,
                    category=template_info.category,
                    tags=",".join(template_info.tags) if template_info.tags else ""
                )
        except Exception as e:
            raise EnvironmentError(f"Failed to update template: {e}")
        
        return template_info
    
    async def remove_template(self, template_name: str, ctx: Context) -> str:
        """Remove a cookiecutter template and its virtual environment.
        
        Args:
            template_name: Name of the template to remove
            ctx: MCP context
        
        Returns:
            A success message
        
        Raises:
            TemplateNotFoundError: If the template is not found
            EnvironmentError: If there's an error removing the template
        """
        # Check if template exists in installed templates
        if template_name in self.templates:
            # Get template info
            template_info = self.templates[template_name]
            
            # Remove template directory
            await ctx.info(f"Removing template directory: {template_info.path}")
            try:
                import shutil
                shutil.rmtree(template_info.path)
            except Exception as e:
                raise EnvironmentError(f"Failed to remove template directory: {e}")
            
            # Remove virtual environment
            await ctx.info(f"Removing virtual environment: {template_info.venv_path}")
            try:
                if os.path.exists(template_info.venv_path):
                    await EnvironmentManager.cleanup_venv(template_info.venv_path)
            except Exception as e:
                raise EnvironmentError(f"Failed to remove virtual environment: {e}")
            
            # Remove template from registry
            del self.templates[template_name]
        
        # Check if template exists in database
        db_template = get_template_by_name(template_name)
        if db_template:
            # Remove from database
            delete_template(template_name)
            
            # Remove from db_templates if present
            if template_name in self.db_templates:
                del self.db_templates[template_name]
        else:
            # Template not found in either location
            if template_name not in self.templates:
                raise TemplateNotFoundError(f"Template '{template_name}' not found")
        
        await ctx.info(f"Template '{template_name}' removed successfully")
        return f"Template '{template_name}' removed successfully"
    
    async def discover_templates(self, ctx: Context) -> List[TemplateInfo]:
        """Discover popular cookiecutter templates from the database.
        
        Args:
            ctx: MCP context
        
        Returns:
            A list of template info objects
        """
        await ctx.info("Discovering templates from database")
        
        # Get templates from database
        db_templates = get_templates_by_category()
        templates = []
        
        for i, db_template in enumerate(db_templates):
            try:
                await ctx.progress(f"Discovering templates ({i+1}/{len(db_templates)})",
                                  (i+1) / len(db_templates) * 100)
            except AttributeError:
                # If progress method is not available, use info method
                await ctx.info(f"Discovering templates ({i+1}/{len(db_templates)})")
            
            # Skip templates that are already installed
            if db_template["name"] in self.templates:
                continue
            
            # Convert database template to model
            template_info = convert_db_template_to_model(db_template)
            templates.append(template_info)
        
        return templates