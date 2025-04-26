"""
Exceptions for the dynamo-mcp system.

This module provides exception classes for the dynamo-mcp system.
"""


class DynamoMCPError(Exception):
    """Base exception for all dynamo-mcp errors."""
    pass


class TemplateNotFoundError(DynamoMCPError):
    """Raised when a template is not found."""
    pass


class TemplateExistsError(DynamoMCPError):
    """Raised when a template already exists."""
    pass


class EnvironmentError(DynamoMCPError):
    """Raised when there's an error with the environment."""
    pass


class ProjectGenerationError(DynamoMCPError):
    """Raised when there's an error generating a project."""
    pass


class InterfaceGenerationError(DynamoMCPError):
    """Raised when there's an error generating an interface."""
    pass


class ConfigurationError(DynamoMCPError):
    """Raised when there's an error with the configuration."""
    pass


class TransportError(DynamoMCPError):
    """Raised when there's an error with the transport."""
    pass