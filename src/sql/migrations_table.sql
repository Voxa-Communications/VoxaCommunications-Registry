-- filepath: /workspaces/VoxaCommunications-Registry/src/sql/migrations_table.sql
-- Creates a table to track applied migrations
CREATE TABLE IF NOT EXISTS schema_migrations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    migration_id VARCHAR(255) UNIQUE NOT NULL,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);