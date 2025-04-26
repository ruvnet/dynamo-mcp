#!/usr/bin/env python
"""
Initialize the template database using the SQL schema file.

This script creates the database tables using the schema.sql file
and then populates the database with default templates.
"""
import os
import sys
import argparse
import sqlite3
from pathlib import Path

# Add parent directory to path to allow importing dynamo_mcp modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from dynamo_mcp.utils.config import CONFIG_DIR
from dynamo_mcp.utils.init_template_db import initialize_database

# Database file path
DB_PATH = os.path.join(CONFIG_DIR, "templates.db")
# SQL schema file path
SQL_SCHEMA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sql", "schema.sql")


def init_db_from_schema(reset: bool = False):
    """
    Initialize the database using the SQL schema file.
    
    Args:
        reset: Whether to reset the database before initialization
    """
    # Create config directory if it doesn't exist
    os.makedirs(CONFIG_DIR, exist_ok=True)
    
    # Remove existing database if reset is True
    if reset and os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"Removed existing database at {DB_PATH}")
    
    # Connect to database (creates it if it doesn't exist)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Read and execute SQL schema
    with open(SQL_SCHEMA_PATH, 'r') as f:
        schema_sql = f.read()
    
    # Execute each statement separately
    for statement in schema_sql.split(';'):
        if statement.strip():
            cursor.execute(statement)
    
    conn.commit()
    conn.close()
    
    print(f"Database schema initialized from {SQL_SCHEMA_PATH}")


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description='Initialize the template database from SQL schema')
    parser.add_argument('--reset', action='store_true', help='Reset the database before initialization')
    parser.add_argument('--schema-only', action='store_true', help='Only initialize schema, do not add templates')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show verbose output')
    args = parser.parse_args()
    
    print("Initializing template database...")
    
    # Initialize database schema
    init_db_from_schema(reset=args.reset)
    
    # Add templates if not schema-only
    if not args.schema_only:
        count, names = initialize_database(reset=False)  # Don't reset again
        
        print(f"Added {count} templates to the database.")
        
        if args.verbose:
            print("\nAdded templates:")
            for name in names:
                print(f"  - {name}")
    
    print("\nDatabase initialization complete.")


if __name__ == "__main__":
    main()