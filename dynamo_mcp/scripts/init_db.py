#!/usr/bin/env python
"""
Initialize the template database with default templates.

This script is used to populate the SQLite database with a comprehensive list
of cookiecutter templates across various categories.
"""
import os
import sys
import argparse

# Add parent directory to path to allow importing dynamo_mcp modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from dynamo_mcp.utils.init_template_db import initialize_database


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description='Initialize the template database')
    parser.add_argument('--reset', action='store_true', help='Reset the database before initialization')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show verbose output')
    args = parser.parse_args()
    
    print("Initializing template database...")
    count, names = initialize_database(reset=args.reset)
    
    print(f"Added {count} templates to the database.")
    
    if args.verbose:
        print("\nAdded templates:")
        for name in names:
            print(f"  - {name}")
    
    print("\nDatabase initialization complete.")


if __name__ == "__main__":
    main()