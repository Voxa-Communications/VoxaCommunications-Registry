-- filepath: /workspaces/VoxaCommunications-Registry/src/sql/nodes_table.sql
DROP TABLE IF EXISTS nodes; -- Something else should be done in production
CREATE TABLE IF NOT EXISTS nodes (
    id VARCHAR(36) PRIMARY KEY,
    creator_id INT NOT NULL,
    ip_address VARCHAR(45) NOT NULL,
    callsign VARCHAR(255) NOT NULL,
    crypto_key TEXT NOT NULL,
    node_type VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    last_seen TIMESTAMP NULL,
    FOREIGN KEY (creator_id) REFERENCES users(id) ON DELETE CASCADE
);