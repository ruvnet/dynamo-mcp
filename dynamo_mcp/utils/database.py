"""
Database module for dynamo-mcp.

This module provides functions for interacting with the SQLite database
that stores template information.
"""
import os
import sqlite3
from typing import List, Dict, Optional, Tuple
from pathlib import Path

from dynamo_mcp.utils.config import CONFIG_DIR
from dynamo_mcp.core.models import TemplateInfo

# Database file path
DB_PATH = os.path.join(CONFIG_DIR, "templates.db")

def ensure_db_exists():
    """Ensure the database file exists and has the correct schema."""
    # Create config directory if it doesn't exist
    os.makedirs(CONFIG_DIR, exist_ok=True)
    
    # Connect to database (creates it if it doesn't exist)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create templates table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS templates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        url TEXT NOT NULL,
        description TEXT,
        category TEXT,
        tags TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create versions table for template versioning
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS template_versions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        template_id INTEGER,
        version TEXT NOT NULL,
        git_hash TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (template_id) REFERENCES templates (id)
    )
    ''')
    
    # Create dependencies table for template dependencies
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS template_dependencies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        template_id INTEGER,
        dependency_id INTEGER,
        optional BOOLEAN DEFAULT 0,
        FOREIGN KEY (template_id) REFERENCES templates (id),
        FOREIGN KEY (dependency_id) REFERENCES templates (id)
    )
    ''')
    
    conn.commit()
    conn.close()

def add_template(name: str, url: str, description: str = "", category: str = "", tags: str = "") -> int:
    """
    Add a template to the database.
    
    Args:
        name: Template name
        url: Template URL
        description: Template description
        category: Template category
        tags: Comma-separated list of tags
        
    Returns:
        The ID of the inserted template
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO templates (name, url, description, category, tags) VALUES (?, ?, ?, ?, ?)",
        (name, url, description, category, tags)
    )
    
    template_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return template_id

def get_template_by_name(name: str) -> Optional[Dict]:
    """
    Get a template by name.
    
    Args:
        name: Template name
        
    Returns:
        Template information as a dictionary, or None if not found
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM templates WHERE name = ?", (name,))
    row = cursor.fetchone()
    
    conn.close()
    
    if row:
        return dict(row)
    return None

def get_templates_by_category(category: Optional[str] = None) -> List[Dict]:
    """
    Get templates filtered by category.
    
    Args:
        category: Category to filter by, or None for all templates
        
    Returns:
        List of template dictionaries
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    if category:
        cursor.execute("SELECT * FROM templates WHERE category = ?", (category,))
    else:
        cursor.execute("SELECT * FROM templates")
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

def get_all_categories() -> List[str]:
    """
    Get all unique categories in the database.
    
    Returns:
        List of category names
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT DISTINCT category FROM templates WHERE category IS NOT NULL AND category != ''")
    categories = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    
    return categories

def search_templates(query: str) -> List[Dict]:
    """
    Search templates by name, description, category, or tags.
    
    Args:
        query: Search query
        
    Returns:
        List of matching template dictionaries
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    search_param = f"%{query}%"
    cursor.execute("""
    SELECT * FROM templates 
    WHERE name LIKE ? 
    OR description LIKE ? 
    OR category LIKE ? 
    OR tags LIKE ?
    """, (search_param, search_param, search_param, search_param))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

def delete_template(name: str) -> bool:
    """
    Delete a template from the database.
    
    Args:
        name: Template name
        
    Returns:
        True if template was deleted, False if not found
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM templates WHERE name = ?", (name,))
    deleted = cursor.rowcount > 0
    
    conn.commit()
    conn.close()
    
    return deleted

def update_template(name: str, **kwargs) -> bool:
    """
    Update a template in the database.
    
    Args:
        name: Template name
        **kwargs: Fields to update (url, description, category, tags)
        
    Returns:
        True if template was updated, False if not found
    """
    valid_fields = {"url", "description", "category", "tags"}
    update_fields = {k: v for k, v in kwargs.items() if k in valid_fields}
    
    if not update_fields:
        return False
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    set_clause = ", ".join([f"{field} = ?" for field in update_fields])
    values = list(update_fields.values())
    values.append(name)
    
    cursor.execute(f"UPDATE templates SET {set_clause} WHERE name = ?", values)
    updated = cursor.rowcount > 0
    
    conn.commit()
    conn.close()
    
    return updated

def convert_db_template_to_model(template_dict: Dict) -> TemplateInfo:
    """
    Convert a template dictionary from the database to a TemplateInfo model.
    
    Args:
        template_dict: Template dictionary from database
        
    Returns:
        TemplateInfo model
    """
    # For templates from the database that haven't been installed yet,
    # path and venv_path will be empty
    return TemplateInfo(
        name=template_dict["name"],
        url=template_dict["url"],
        description=template_dict["description"] or "",
        path="",
        venv_path="",
        category=template_dict["category"] or "",
        tags=template_dict["tags"].split(",") if template_dict["tags"] else []
    )

def clear_database() -> None:
    """Clear all data from the database (for testing purposes)."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM template_dependencies")
    cursor.execute("DELETE FROM template_versions")
    cursor.execute("DELETE FROM templates")
    
    conn.commit()
    conn.close()