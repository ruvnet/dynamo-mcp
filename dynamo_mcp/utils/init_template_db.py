"""
Initialize the template database with default templates.

This script populates the SQLite database with a comprehensive list of
cookiecutter templates across various categories.
"""
import csv
import os
import sys
from io import StringIO
from typing import List, Dict, Tuple

from dynamo_mcp.utils.database import ensure_db_exists, add_template, clear_database

# Default templates data as CSV
DEFAULT_TEMPLATES = """
category,url
Python,"https://github.com/audreyfeldroy/cookiecutter-pypackage"
Python,"https://github.com/cjolowicz/cookiecutter-hypermodern-python"
Data Science,"https://github.com/drivendataorg/cookiecutter-data-science"
Django,"https://github.com/cookiecutter/cookiecutter-django"
Flask,"https://github.com/cookiecutter-flask/cookiecutter-flask"
FastAPI,"https://github.com/arthurhenrique/cookiecutter-fastapi"
React,"https://github.com/vchaptsev/cookiecutter-django-vue"
AWS,"https://github.com/aws-samples/cookiecutter-aws-sam-python"
Machine Learning,"https://github.com/fmind/cookiecutter-mlops-package"
Docker,"https://github.com/docker-science/cookiecutter-docker-science"
Jupyter,"https://github.com/jupyter-widgets/widget-cookiecutter"
Ansible,"https://github.com/iknite/cookiecutter-ansible-role"
Terraform,"https://github.com/TerraformInDepth/terraform-module-cookiecutter"
Rust,"https://github.com/microsoft/cookiecutter-rust-actix-clean-architecture"
Go,"https://github.com/lacion/cookiecutter-golang"
JavaScript,"https://github.com/jupyterlab/extension-cookiecutter-ts"
TypeScript,"https://github.com/jupyterlab/mimerender-cookiecutter-ts"
C++,"https://github.com/ssciwr/cookiecutter-cpp-project"
Qt,"https://github.com/agateau/cookiecutter-qt-app"
PyTorch,"https://github.com/khornlund/cookiecutter-pytorch"
TensorFlow,"https://github.com/tdeboissiere/cookiecutter-deeplearning"
Jupyter Book,"https://github.com/executablebooks/cookiecutter-jupyter-book"
Streamlit,"https://github.com/andymcdgeo/cookiecutter-streamlit"
FastAPI-PostgreSQL,"https://github.com/tiangolo/full-stack-fastapi-postgresql"
Django-REST,"https://github.com/agconti/cookiecutter-django-rest"
Science,"https://github.com/jbusecke/cookiecutter-science-project"
Bioinformatics,"https://github.com/maxplanck-ie/cookiecutter-bioinformatics-project"
LaTeX,"https://github.com/selimb/cookiecutter-latex-article"
Kotlin,"https://github.com/m-x-k/cookiecutter-kotlin-gradle"
Home Assistant,"https://github.com/oncleben31/cookiecutter-homeassistant-custom-component"
.NET,"https://github.com/aws-samples/cookiecutter-aws-sam-dotnet"
Ruby,"https://github.com/customink/cookiecutter-ruby"
Scala,"https://github.com/jpzk/cookiecutter-scala-spark"
Elixir,"https://github.com/mattvonrocketstein/cookiecutter-elixir-project"
R,"https://github.com/associatedpress/cookiecutter-r-project"
Julia,"https://github.com/xtensor-stack/xtensor-julia-cookiecutter"
MATLAB,"https://github.com/gvoysey/cookiecutter-python-scientific"
Arduino,"https://github.com/BrianPugh/cookiecutter-esp32-webserver"
ROS,"https://github.com/ros-industrial/cookiecutter-ros-industrial"
Kubernetes,"https://github.com/uzi0espil/cookiecutter-django-k8s"
Serverless,"https://github.com/ran-isenberg/cookiecutter-serverless-python"
Polars,"https://github.com/MarcoGorelli/cookiecutter-polars-plugins"
ML Research,"https://github.com/csinva/cookiecutter-ml-research"
Education,"https://github.com/mikeckennedy/cookiecutter-course"
Documentation,"https://github.com/pawamoy/cookiecutter-awesome"
Chrome Extension,"https://github.com/audreyfeldroy/cookiecutter-chrome-extension"
Blender,"https://github.com/joshuaskelly/cookiecutter-blender-addon"
Unity,"https://github.com/hackebrot/cookiecutter-kivy"
Godot,"https://github.com/lockie/cookiecutter-lisp-game"
SuperCollider,"https://github.com/supercollider/cookiecutter-supercollider-plugin"
QGIS,"https://github.com/GispoCoding/cookiecutter-qgis-plugin"
WordPress,"https://github.com/Jean-Zombie/cookiecutter-django-wagtail"
Shopify,"https://github.com/awesto/cookiecutter-django-shop"
Moodle,"https://github.com/openedx/edx-cookiecutters"
Salesforce,"https://github.com/datacoves/cookiecutter-dbt"
Zapier,"https://github.com/narfman0/cookiecutter-mobile-backend"
"""

def parse_csv_data(csv_data: str) -> List[Dict[str, str]]:
    """
    Parse CSV data into a list of dictionaries.
    
    Args:
        csv_data: CSV data as a string
        
    Returns:
        List of dictionaries with template information
    """
    templates = []
    csv_file = StringIO(csv_data.strip())
    reader = csv.DictReader(csv_file)
    
    for row in reader:
        # Extract template name from URL
        url = row['url'].strip('"')
        name = url.split('/')[-1]
        
        # Remove .git suffix if present
        if name.endswith('.git'):
            name = name[:-4]
            
        # Remove cookiecutter- prefix if present
        if name.startswith('cookiecutter-'):
            name = name[len('cookiecutter-'):]
            
        # Create template dictionary
        template = {
            'name': name,
            'url': url,
            'category': row['category'].strip('"'),
            'description': f"Cookiecutter template for {row['category'].strip('\"')} projects"
        }
        
        templates.append(template)
        
    return templates

def initialize_database(reset: bool = False) -> Tuple[int, List[str]]:
    """
    Initialize the database with default templates.
    
    Args:
        reset: Whether to reset the database before initialization
        
    Returns:
        Tuple of (number of templates added, list of template names)
    """
    # Ensure database exists
    ensure_db_exists()
    
    # Reset database if requested
    if reset:
        clear_database()
    
    # Parse template data
    templates = parse_csv_data(DEFAULT_TEMPLATES)
    
    # Add templates to database
    added_count = 0
    template_names = []
    
    for template in templates:
        try:
            add_template(
                name=template['name'],
                url=template['url'],
                description=template['description'],
                category=template['category']
            )
            added_count += 1
            template_names.append(template['name'])
        except Exception as e:
            print(f"Error adding template {template['name']}: {e}")
    
    return added_count, template_names

def main():
    """Main entry point for the script."""
    reset = len(sys.argv) > 1 and sys.argv[1] == '--reset'
    
    print("Initializing template database...")
    count, names = initialize_database(reset=reset)
    
    print(f"Added {count} templates to the database.")
    print("Template categories:")
    
    # Group templates by category for display
    templates_by_category = {}
    for template in parse_csv_data(DEFAULT_TEMPLATES):
        category = template['category']
        if category not in templates_by_category:
            templates_by_category[category] = []
        templates_by_category[category].append(template['name'])
    
    for category, templates in sorted(templates_by_category.items()):
        print(f"  {category}: {len(templates)} templates")
    
    print("\nDatabase initialization complete.")

if __name__ == "__main__":
    main()