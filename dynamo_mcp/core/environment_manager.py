"""
Environment Manager for the dynamo-mcp system.

This module provides functionality for creating and managing virtual environments
for cookiecutter templates.
"""
import os
import sys
import shutil
import asyncio
import subprocess
import platform
from pathlib import Path
from typing import Optional, Union

from dynamo_mcp.utils.exceptions import EnvironmentError


class EnvironmentManager:
    """Manager for virtual environments."""
    
    @staticmethod
    def create_venv(venv_path: Union[str, Path]) -> None:
        """Create a virtual environment.
        
        Args:
            venv_path: Path to create the virtual environment at
        
        Raises:
            EnvironmentError: If there's an error creating the virtual environment
        """
        try:
            # Convert string to Path if necessary
            if isinstance(venv_path, str):
                venv_path = Path(venv_path)
            
            # Create directory if it doesn't exist
            venv_path.mkdir(parents=True, exist_ok=True)
            
            # Create virtual environment
            subprocess.run(
                [sys.executable, "-m", "venv", str(venv_path)],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        except subprocess.CalledProcessError as e:
            raise EnvironmentError(f"Failed to create virtual environment: {e.stderr.decode()}")
        except Exception as e:
            raise EnvironmentError(f"Failed to create virtual environment: {e}")
    
    @staticmethod
    async def cleanup_venv(venv_path: Union[str, Path]) -> None:
        """Clean up a virtual environment.
        
        Args:
            venv_path: Path to the virtual environment
        
        Raises:
            EnvironmentError: If there's an error cleaning up the virtual environment
        """
        try:
            # Convert string to Path if necessary
            if isinstance(venv_path, str):
                venv_path = Path(venv_path)
            
            # Remove directory
            if venv_path.exists():
                shutil.rmtree(venv_path)
        except Exception as e:
            raise EnvironmentError(f"Failed to clean up virtual environment: {e}")
    
    @staticmethod
    def _get_python_path(venv_path: Union[str, Path]) -> Path:
        """Get the path to the Python executable in a virtual environment.
        
        Args:
            venv_path: Path to the virtual environment
        
        Returns:
            Path to the Python executable
        
        Raises:
            EnvironmentError: If the Python executable is not found
        """
        # Convert string to Path if necessary
        if isinstance(venv_path, str):
            venv_path = Path(venv_path)
        
        # Determine Python executable path based on platform
        if platform.system() == "Windows":
            python_path = venv_path / "Scripts" / "python.exe"
        else:
            python_path = venv_path / "bin" / "python"
        
        # Check if Python executable exists
        if not python_path.exists():
            raise EnvironmentError(f"Python executable not found in virtual environment: {venv_path}")
        
        return python_path
    
    @staticmethod
    async def run_in_venv(venv_path: Union[str, Path], command: str, *args: str) -> str:
        """Run a command in a virtual environment.
        
        Args:
            venv_path: Path to the virtual environment
            command: Command to run
            args: Arguments for the command
        
        Returns:
            Command output
        
        Raises:
            EnvironmentError: If there's an error running the command
        """
        try:
            # Convert string to Path if necessary
            if isinstance(venv_path, str):
                venv_path = Path(venv_path)
            
            # Get Python executable path
            python_path = EnvironmentManager._get_python_path(venv_path)
            
            # Run command
            process = await asyncio.create_subprocess_exec(
                str(python_path), "-m", command, *args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            # Check if command succeeded
            if process.returncode != 0:
                raise EnvironmentError(f"Command failed: {stderr.decode()}")
            
            return stdout.decode()
        except Exception as e:
            raise EnvironmentError(f"Failed to run command in virtual environment: {e}")
    
    @staticmethod
    async def install_package(venv_path: Union[str, Path], package: str) -> None:
        """Install a package in a virtual environment.
        
        Args:
            venv_path: Path to the virtual environment
            package: Package to install
        
        Raises:
            EnvironmentError: If there's an error installing the package
        """
        try:
            # Convert string to Path if necessary
            if isinstance(venv_path, str):
                venv_path = Path(venv_path)
            
            # Get Python executable path
            python_path = EnvironmentManager._get_python_path(venv_path)
            
            # Install package
            process = await asyncio.create_subprocess_exec(
                str(python_path), "-m", "pip", "install", package,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            # Check if installation succeeded
            if process.returncode != 0:
                raise EnvironmentError(f"Failed to install package: {stderr.decode()}")
        except Exception as e:
            raise EnvironmentError(f"Failed to install package: {e}")