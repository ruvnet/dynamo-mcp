"""
Models for the dynamo-mcp system.

This module provides data models for the dynamo-mcp system.
"""
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field


class TemplateInfo(BaseModel):
    """Information about a cookiecutter template."""
    
    name: str = Field(..., description="The name of the template")
    url: str = Field(..., description="The URL of the template repository")
    description: str = Field("", description="A description of the template")
    path: str = Field(..., description="The path to the template directory")
    venv_path: str = Field(..., description="The path to the virtual environment")
    category: str = Field("", description="The category of the template")
    tags: List[str] = Field(default_factory=list, description="Tags for the template")


class TemplateVariable(BaseModel):
    """A variable for a cookiecutter template."""
    
    name: str = Field(..., description="The name of the variable")
    type: str = Field(..., description="The type of the variable")
    description: str = Field("", description="A description of the variable")
    default: Any = Field(None, description="The default value of the variable")
    options: Optional[List[Any]] = Field(None, description="The options for the variable")


class CreateProjectRequest(BaseModel):
    """Request to create a project from a template."""
    
    template_name: str = Field(..., description="The name of the template to use")
    output_dir: str = Field(..., description="The directory to output the project to")
    variables: Dict[str, Any] = Field(..., description="The variables to use for the template")