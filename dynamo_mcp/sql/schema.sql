-- Template Database Schema

-- Templates table
CREATE TABLE IF NOT EXISTS templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    url TEXT NOT NULL,
    description TEXT,
    category TEXT,
    tags TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Template versions table
CREATE TABLE IF NOT EXISTS template_versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    template_id INTEGER,
    version TEXT NOT NULL,
    git_hash TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (template_id) REFERENCES templates (id)
);

-- Template dependencies table
CREATE TABLE IF NOT EXISTS template_dependencies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    template_id INTEGER,
    dependency_id INTEGER,
    optional BOOLEAN DEFAULT 0,
    FOREIGN KEY (template_id) REFERENCES templates (id),
    FOREIGN KEY (dependency_id) REFERENCES templates (id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_templates_name ON templates(name);
CREATE INDEX IF NOT EXISTS idx_templates_category ON templates(category);
CREATE INDEX IF NOT EXISTS idx_template_versions_template_id ON template_versions(template_id);
CREATE INDEX IF NOT EXISTS idx_template_dependencies_template_id ON template_dependencies(template_id);
CREATE INDEX IF NOT EXISTS idx_template_dependencies_dependency_id ON template_dependencies(dependency_id);