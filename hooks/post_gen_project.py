#!/usr/bin/env python
import os
import subprocess
import sys

PROJECT_DIRECTORY = os.path.realpath(os.path.curdir)

def remove_file(filepath):
    os.remove(os.path.join(PROJECT_DIRECTORY, filepath))

def initialize_git():
    """Initialize git repository"""
    try:
        subprocess.check_call(['git', 'init'], cwd=PROJECT_DIRECTORY)
        print("✅ Git repository initialized")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️ Could not initialize git repository")

def setup_virtual_environment():
    """Set up a virtual environment"""
    try:
        subprocess.check_call([sys.executable, '-m', 'venv', 'venv'], cwd=PROJECT_DIRECTORY)
        print("✅ Virtual environment created")
        
        # Determine the pip path based on the OS
        if os.name == 'nt':  # Windows
            pip_path = os.path.join(PROJECT_DIRECTORY, 'venv', 'Scripts', 'pip')
        else:  # Unix/Linux/MacOS
            pip_path = os.path.join(PROJECT_DIRECTORY, 'venv', 'bin', 'pip')
        
        # Install dependencies
        subprocess.check_call([pip_path, 'install', '-e', '.'], cwd=PROJECT_DIRECTORY)
        print("✅ Dependencies installed")
    except subprocess.CalledProcessError:
        print("⚠️ Could not set up virtual environment")

def main():
    if '{{ cookiecutter.use_pytest }}' != 'y':
        remove_file('pytest.ini')
        remove_file('tests/test_basic.py')
    
    if '{{ cookiecutter.use_black }}' != 'y':
        remove_file('.pre-commit-config.yaml')
    
    if '{{ cookiecutter.open_source_license }}' == 'Not open source':
        remove_file('LICENSE')
    
    print("\n🎉 Project '{{ cookiecutter.project_name }}' created successfully!")
    print("\nNext steps:")
    print("1. Change into the project directory: cd {{ cookiecutter.project_slug }}")
    print("2. Initialize git repository (if not already done)")
    print("3. Create a virtual environment (if not already done)")
    print("4. Install dependencies: pip install -e .")
    print("5. Start the MCP server: python -m {{ cookiecutter.project_slug }}.main")
    
    # Initialize git and setup virtual environment
    initialize_git()
    setup_virtual_environment()

if __name__ == '__main__':
    main()