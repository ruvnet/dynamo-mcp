"""
Tests for the database module.

This module contains tests for the database module.
"""
import os
import sys
import unittest
import tempfile
import sqlite3
from pathlib import Path

# Add parent directory to path to allow importing dynamo_mcp modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dynamo_mcp.utils.database import (
    ensure_db_exists, add_template, get_template_by_name,
    get_templates_by_category, get_all_categories, search_templates,
    delete_template, update_template, convert_db_template_to_model
)
from dynamo_mcp.utils.init_template_db import initialize_database, parse_csv_data
from dynamo_mcp.core.models import TemplateInfo


class TestDatabase(unittest.TestCase):
    """Test case for the database module."""
    
    def setUp(self):
        """Set up the test case."""
        # Create a temporary directory for the database
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "templates.db")
        
        # Set the database path in the module
        import dynamo_mcp.utils.database as db_module
        self.original_db_path = db_module.DB_PATH
        db_module.DB_PATH = self.db_path
        
        # Ensure the database exists
        ensure_db_exists()
    
    def tearDown(self):
        """Tear down the test case."""
        # Restore the original database path
        import dynamo_mcp.utils.database as db_module
        db_module.DB_PATH = self.original_db_path
        
        # Clean up the temporary directory
        self.temp_dir.cleanup()
    
    def test_add_template(self):
        """Test adding a template to the database."""
        # Add a template
        template_id = add_template(
            name="test-template",
            url="https://github.com/test/test-template.git",
            description="Test template",
            category="Test",
            tags="test,template"
        )
        
        # Check that the template was added
        self.assertIsNotNone(template_id)
        
        # Get the template
        template = get_template_by_name("test-template")
        
        # Check that the template was retrieved correctly
        self.assertIsNotNone(template)
        self.assertEqual(template["name"], "test-template")
        self.assertEqual(template["url"], "https://github.com/test/test-template.git")
        self.assertEqual(template["description"], "Test template")
        self.assertEqual(template["category"], "Test")
        self.assertEqual(template["tags"], "test,template")
    
    def test_get_templates_by_category(self):
        """Test getting templates by category."""
        # Add templates in different categories
        add_template(
            name="test-template-1",
            url="https://github.com/test/test-template-1.git",
            description="Test template 1",
            category="Test1",
            tags="test,template"
        )
        
        add_template(
            name="test-template-2",
            url="https://github.com/test/test-template-2.git",
            description="Test template 2",
            category="Test2",
            tags="test,template"
        )
        
        add_template(
            name="test-template-3",
            url="https://github.com/test/test-template-3.git",
            description="Test template 3",
            category="Test1",
            tags="test,template"
        )
        
        # Get templates by category
        templates1 = get_templates_by_category("Test1")
        templates2 = get_templates_by_category("Test2")
        all_templates = get_templates_by_category()
        
        # Check that the templates were retrieved correctly
        self.assertEqual(len(templates1), 2)
        self.assertEqual(len(templates2), 1)
        self.assertEqual(len(all_templates), 3)
    
    def test_get_all_categories(self):
        """Test getting all categories."""
        # Add templates in different categories
        add_template(
            name="test-template-1",
            url="https://github.com/test/test-template-1.git",
            description="Test template 1",
            category="Test1",
            tags="test,template"
        )
        
        add_template(
            name="test-template-2",
            url="https://github.com/test/test-template-2.git",
            description="Test template 2",
            category="Test2",
            tags="test,template"
        )
        
        # Get all categories
        categories = get_all_categories()
        
        # Check that the categories were retrieved correctly
        self.assertEqual(len(categories), 2)
        self.assertIn("Test1", categories)
        self.assertIn("Test2", categories)
    
    def test_search_templates(self):
        """Test searching templates."""
        # Add templates
        add_template(
            name="python-package",
            url="https://github.com/test/python-package.git",
            description="Python package template",
            category="Python",
            tags="python,package"
        )
        
        add_template(
            name="django-app",
            url="https://github.com/test/django-app.git",
            description="Django application template",
            category="Django",
            tags="python,django,web"
        )
        
        # Search templates
        python_templates = search_templates("python")
        django_templates = search_templates("django")
        web_templates = search_templates("web")
        
        # Check that the templates were retrieved correctly
        self.assertEqual(len(python_templates), 2)  # Both have "python" in tags
        self.assertEqual(len(django_templates), 1)  # Only one has "django" in name/tags
        self.assertEqual(len(web_templates), 1)     # Only one has "web" in tags
    
    def test_update_template(self):
        """Test updating a template."""
        # Add a template
        add_template(
            name="test-template",
            url="https://github.com/test/test-template.git",
            description="Test template",
            category="Test",
            tags="test,template"
        )
        
        # Update the template
        updated = update_template(
            "test-template",
            url="https://github.com/test/updated-template.git",
            description="Updated test template",
            category="Updated",
            tags="updated,test,template"
        )
        
        # Check that the template was updated
        self.assertTrue(updated)
        
        # Get the updated template
        template = get_template_by_name("test-template")
        
        # Check that the template was updated correctly
        self.assertEqual(template["url"], "https://github.com/test/updated-template.git")
        self.assertEqual(template["description"], "Updated test template")
        self.assertEqual(template["category"], "Updated")
        self.assertEqual(template["tags"], "updated,test,template")
    
    def test_delete_template(self):
        """Test deleting a template."""
        # Add a template
        add_template(
            name="test-template",
            url="https://github.com/test/test-template.git",
            description="Test template",
            category="Test",
            tags="test,template"
        )
        
        # Delete the template
        deleted = delete_template("test-template")
        
        # Check that the template was deleted
        self.assertTrue(deleted)
        
        # Try to get the deleted template
        template = get_template_by_name("test-template")
        
        # Check that the template was not found
        self.assertIsNone(template)
    
    def test_convert_db_template_to_model(self):
        """Test converting a database template to a model."""
        # Create a template dictionary
        template_dict = {
            "name": "test-template",
            "url": "https://github.com/test/test-template.git",
            "description": "Test template",
            "category": "Test",
            "tags": "test,template"
        }
        
        # Convert the template to a model
        template_model = convert_db_template_to_model(template_dict)
        
        # Check that the model was created correctly
        self.assertIsInstance(template_model, TemplateInfo)
        self.assertEqual(template_model.name, "test-template")
        self.assertEqual(template_model.url, "https://github.com/test/test-template.git")
        self.assertEqual(template_model.description, "Test template")
        self.assertEqual(template_model.category, "Test")
        self.assertEqual(template_model.tags, ["test", "template"])
        self.assertEqual(template_model.path, "")
        self.assertEqual(template_model.venv_path, "")
    
    def test_parse_csv_data(self):
        """Test parsing CSV data."""
        # CSV data
        csv_data = """
category,url
Python,"https://github.com/audreyfeldroy/cookiecutter-pypackage"
Django,"https://github.com/cookiecutter/cookiecutter-django"
"""
        
        # Parse the CSV data
        templates = parse_csv_data(csv_data)
        
        # Check that the templates were parsed correctly
        self.assertEqual(len(templates), 2)
        self.assertEqual(templates[0]["name"], "pypackage")
        self.assertEqual(templates[0]["url"], "https://github.com/audreyfeldroy/cookiecutter-pypackage")
        self.assertEqual(templates[0]["category"], "Python")
        self.assertEqual(templates[1]["name"], "django")
        self.assertEqual(templates[1]["url"], "https://github.com/cookiecutter/cookiecutter-django")
        self.assertEqual(templates[1]["category"], "Django")
    
    def test_initialize_database(self):
        """Test initializing the database."""
        # Initialize the database
        count, names = initialize_database()
        
        # Check that templates were added
        self.assertGreater(count, 0)
        self.assertGreater(len(names), 0)
        
        # Check that the templates can be retrieved
        templates = get_templates_by_category()
        
        # Check that the templates were retrieved correctly
        self.assertEqual(len(templates), count)
        
        # Reset and reinitialize the database
        count2, names2 = initialize_database(reset=True)
        
        # Check that templates were added again
        self.assertGreater(count2, 0)
        self.assertGreater(len(names2), 0)


if __name__ == "__main__":
    unittest.main()