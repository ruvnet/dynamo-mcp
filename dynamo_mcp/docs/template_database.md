# Template Database

The dynamo-mcp system includes a SQLite database for managing cookiecutter templates. This database provides several advantages over the previous file-based approach:

1. **Comprehensive Template Library**: Includes a large collection of pre-defined templates across various categories
2. **Category-Based Organization**: Templates are organized by category for easier discovery
3. **Search Capabilities**: Search templates by name, description, category, or tags
4. **Template Metadata**: Store additional metadata like categories and tags
5. **Versioning Support**: Track template versions and updates

## Database Schema

The database includes the following tables:

### Templates Table

Stores basic information about templates:

| Column      | Type      | Description                           |
|-------------|-----------|---------------------------------------|
| id          | INTEGER   | Primary key                           |
| name        | TEXT      | Template name                         |
| url         | TEXT      | Template repository URL               |
| description | TEXT      | Template description                  |
| category    | TEXT      | Template category                     |
| tags        | TEXT      | Comma-separated list of tags          |
| created_at  | TIMESTAMP | Creation timestamp                    |

### Template Versions Table

Tracks versions of templates:

| Column      | Type      | Description                           |
|-------------|-----------|---------------------------------------|
| id          | INTEGER   | Primary key                           |
| template_id | INTEGER   | Foreign key to templates table        |
| version     | TEXT      | Version string (e.g., "1.0.0")        |
| git_hash    | TEXT      | Git commit hash                       |
| created_at  | TIMESTAMP | Creation timestamp                    |

### Template Dependencies Table

Tracks dependencies between templates:

| Column        | Type      | Description                           |
|---------------|-----------|---------------------------------------|
| id            | INTEGER   | Primary key                           |
| template_id   | INTEGER   | Foreign key to templates table        |
| dependency_id | INTEGER   | Foreign key to templates table        |
| optional      | BOOLEAN   | Whether the dependency is optional    |

## Using the Database

### Initializing the Database

The database is automatically initialized when the MCP server starts. You can also manually initialize or reset the database using the following command-line options:

```bash
# Initialize the database with default templates
python -m dynamo_mcp.main --init-db

# Reset the database and reinitialize with default templates
python -m dynamo_mcp.main --reset-db
```

You can also use the dedicated initialization script:

```bash
# Initialize the database
python -m dynamo_mcp.scripts.init_db

# Reset the database
python -m dynamo_mcp.scripts.init_db --reset

# Show verbose output
python -m dynamo_mcp.scripts.init_db --verbose
```

### Template Categories

The default template library includes templates in the following categories:

- Python
- Data Science
- Django
- Flask
- FastAPI
- React
- AWS
- Machine Learning
- Docker
- Jupyter
- Ansible
- Terraform
- Rust
- Go
- JavaScript
- TypeScript
- C++
- Qt
- PyTorch
- TensorFlow
- And many more...

### API Integration

The database is integrated with the TemplateRegistry class, which provides methods for:

- Listing templates by category
- Searching templates
- Adding new templates
- Updating templates
- Removing templates

## Extending the Database

You can extend the template database by:

1. Adding new templates to the `DEFAULT_TEMPLATES` constant in `dynamo_mcp/utils/init_template_db.py`
2. Creating a custom initialization script that adds templates from a different source
3. Using the MCP API to add templates programmatically

## Future Enhancements

Planned enhancements for the template database include:

1. **Template Versioning**: Track and manage multiple versions of templates
2. **Template Composition**: Create templates that include other templates
3. **Dependency Management**: Track and resolve dependencies between templates
4. **Template Validation**: Validate templates against a schema
5. **Template Testing**: Automated testing of templates