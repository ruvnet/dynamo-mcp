#!/usr/bin/env python
"""
Script to convert the current project structure to a cookiecutter template structure.
This will create a new directory structure with template variables.
"""
import os
import shutil
import sys
from pathlib import Path

def create_template_structure():
    """Create the cookiecutter template structure."""
    # Define paths
    current_dir = Path.cwd()
    template_dir = current_dir / "{{cookiecutter.project_slug}}"
    
    # Create the template directory
    if template_dir.exists():
        print(f"Template directory {template_dir} already exists. Please remove it first.")
        sys.exit(1)
    
    template_dir.mkdir(parents=True, exist_ok=True)
    
    # Files/directories to exclude from copying
    exclude = [
        ".git",
        ".github",
        "venv",
        "env",
        "__pycache__",
        "{{cookiecutter.project_slug}}",
        "cookiecutter.json",
        "hooks",
        "scripts/convert_to_template.py",
        ".pytest_cache",
        ".ruff_cache",
        ".mypy_cache",
        "dist",
        "build",
        "*.egg-info",
    ]
    
    # Copy all files and directories to the template directory
    for item in current_dir.iterdir():
        # Skip excluded items
        if any(str(item).endswith(exc) or str(item) == exc for exc in exclude):
            continue
        
        # Copy the item
        if item.is_dir():
            shutil.copytree(item, template_dir / item.name, 
                           ignore=shutil.ignore_patterns(*exclude))
        else:
            shutil.copy2(item, template_dir / item.name)
    
    # Replace hardcoded project names with template variables
    replace_in_files(template_dir, "dynamo_mcp", "{{cookiecutter.project_slug}}")
    replace_in_files(template_dir, "Dynamo MCP", "{{cookiecutter.project_name}}")
    
    print(f"Template structure created at {template_dir}")
    print("Next steps:")
    print("1. Review the template structure")
    print("2. Test the template with: cookiecutter .")
    print("3. Push to GitHub")

def replace_in_files(directory, old_text, new_text):
    """Replace text in all files in the directory."""
    for root, _, files in os.walk(directory):
        for file in files:
            # Skip binary files
            if file.endswith(('.pyc', '.png', '.jpg', '.jpeg', '.gif', '.pdf', '.zip')):
                continue
            
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Replace the text
                if old_text in content:
                    content = content.replace(old_text, new_text)
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
            except UnicodeDecodeError:
                # Skip files that can't be decoded as text
                continue

if __name__ == "__main__":
    create_template_structure()