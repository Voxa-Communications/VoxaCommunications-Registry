"""
Migration: Create Nodes Table
Created at: 2025-05-21T00:00:01
"""

description = "Create nodes table for node registration"

def upgrade(cursor):
    """
    Apply the migration to create the nodes table.
    
    Args:
        cursor: Database cursor to execute SQL statements
    """
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS nodes (
        id VARCHAR(36) PRIMARY KEY,
        creator_id VARCHAR(36) NOT NULL,
        ip_address VARCHAR(45) NOT NULL,
        callsign VARCHAR(255) NOT NULL,
        crypto_key TEXT NOT NULL,
        node_type VARCHAR(50) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        is_active BOOLEAN DEFAULT TRUE,
        last_seen TIMESTAMP NULL
    );
    """)
    
def downgrade(cursor):
    """
    Revert the migration by dropping the nodes table.
    
    Args:
        cursor: Database cursor to execute SQL statements
    """
    cursor.execute("DROP TABLE IF EXISTS nodes;")