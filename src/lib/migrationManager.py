import os
import re
import importlib
import inspect
import time
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from util.logging import log
from util.sqlExecutor import SQLExecutor

class MigrationManager:
    """
    Handles database schema migrations to allow controlled schema evolution.
    """
    
    def __init__(self, migrations_dir: str = "src/migrations"):
        self.logger = log()
        self.migrations_dir = migrations_dir
        self.applied_migrations = {}
        self.available_migrations = {}
        self.logger.info(f"MigrationManager initialized with migrations directory: {migrations_dir}")
        
        # Ensure migrations directory exists
        if not os.path.exists(migrations_dir):
            os.makedirs(migrations_dir)
            self.logger.info(f"Created migrations directory: {migrations_dir}")
            
        # Create migrations table if it doesn't exist
        self._create_migrations_table()

    def _create_migrations_table(self) -> None:
        """
        Creates the migrations tracking table if it doesn't exist.
        """
        try:
            sql_executor = SQLExecutor("migrations_table", None)
            sql_executor.execute_sql()
            self.logger.info("Migrations table created/verified successfully")
        except Exception as e:
            self.logger.error(f"Error creating migrations table: {e}")
            raise e

    def _load_applied_migrations(self) -> None:
        """
        Loads the list of already applied migrations from the database.
        """
        try:
            sql = "SELECT migration_id, applied_at, description FROM schema_migrations ORDER BY id ASC;"
            sql_executor = SQLExecutor("", None)  # Using raw SQL here
            sql_executor.DBManager.cursor.execute(sql)
            results = sql_executor.DBManager.cursor.fetchall()
            
            self.applied_migrations = {row[0]: {"applied_at": row[1], "description": row[2]} for row in results}
            self.logger.info(f"Loaded {len(self.applied_migrations)} applied migrations")
        except Exception as e:
            self.logger.error(f"Error loading applied migrations: {e}")
            raise e

    def _scan_available_migrations(self) -> None:
        """
        Scans the migrations directory for available migration files.
        """
        if not os.path.exists(self.migrations_dir):
            self.logger.warning(f"Migrations directory not found: {self.migrations_dir}")
            return
            
        migration_files = [f for f in os.listdir(self.migrations_dir) 
                          if f.endswith('.py') and re.match(r'^\d{14}_\w+\.py$', f)]
        
        self.available_migrations = {}
        for filename in migration_files:
            migration_id = filename[:-3]  # Remove .py extension
            module_path = f"{self.migrations_dir.replace('/', '.')}.{migration_id}"
            
            try:
                module = importlib.import_module(module_path)
                if hasattr(module, 'upgrade') and callable(module.upgrade):
                    description = getattr(module, 'description', 'No description provided')
                    self.available_migrations[migration_id] = {
                        "module": module,
                        "description": description
                    }
                else:
                    self.logger.warning(f"Migration {migration_id} is missing an upgrade function")
            except ImportError as e:
                self.logger.error(f"Error importing migration {migration_id}: {e}")
                
        self.logger.info(f"Found {len(self.available_migrations)} available migrations")

    def get_pending_migrations(self) -> List[str]:
        """
        Returns a list of migrations that have not been applied yet.
        
        Returns:
            List of migration IDs that need to be applied.
        """
        self._load_applied_migrations()
        self._scan_available_migrations()
        
        # Find migrations that aren't in the applied list
        pending = [m_id for m_id in self.available_migrations if m_id not in self.applied_migrations]
        # Sort by timestamp to ensure proper order
        pending.sort()
        
        return pending

    def create_migration(self, name: str) -> str:
        """
        Creates a new migration file with a timestamp prefix.
        
        Args:
            name: A descriptive name for the migration (will be used in filename)
            
        Returns:
            The path to the created migration file
        """
        # Generate timestamp (YYYYMMDDhhmmss format)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        # Convert name to snake_case and sanitize
        safe_name = re.sub(r'[^a-zA-Z0-9_]', '', name.replace(' ', '_').lower())
        filename = f"{timestamp}_{safe_name}.py"
        filepath = os.path.join(self.migrations_dir, filename)
        
        # Create migration template
        template = f'''"""
Migration: {name}
Created at: {datetime.now().isoformat()}
"""

description = "{name}"

def upgrade(cursor):
    """
    Apply the migration.
    
    Args:
        cursor: Database cursor to execute SQL statements
    """
    # TODO: Add your migration SQL here
    # Example:
    # cursor.execute("ALTER TABLE users ADD COLUMN last_login TIMESTAMP;")
    pass
    
def downgrade(cursor):
    """
    Revert the migration.
    
    Args:
        cursor: Database cursor to execute SQL statements
    """
    # TODO: Add code to revert the migration
    # Example:
    # cursor.execute("ALTER TABLE users DROP COLUMN last_login;")
    pass
'''
        
        # Create migrations dir if it doesn't exist
        os.makedirs(self.migrations_dir, exist_ok=True)
        
        # Write the file
        with open(filepath, 'w') as f:
            f.write(template)
            
        self.logger.info(f"Created new migration: {filepath}")
        return filepath

    def apply_migrations(self, target: Optional[str] = None) -> List[str]:
        """
        Applies all pending migrations or up to a target migration.
        
        Args:
            target: Optional migration ID to migrate up to.
            
        Returns:
            List of applied migration IDs.
        """
        pending = self.get_pending_migrations()
        if not pending:
            self.logger.info("No pending migrations to apply")
            return []
            
        applied = []
        try:
            for migration_id in pending:
                if target and migration_id > target:
                    # Stop if we've reached the target
                    break
                    
                migration = self.available_migrations[migration_id]
                module = migration["module"]
                
                self.logger.info(f"Applying migration: {migration_id} - {migration['description']}")
                sql_executor = SQLExecutor("", None)  # Using raw SQL here
                cursor = sql_executor.DBManager.cursor
                
                try:
                    # Apply the migration
                    start_time = time.time()
                    module.upgrade(cursor)
                    sql_executor.DBManager.connection.commit()
                    duration = time.time() - start_time
                    
                    # Record the migration
                    record_sql = """
                    INSERT INTO schema_migrations (migration_id, applied_at, description)
                    VALUES (%s, %s, %s);
                    """
                    cursor.execute(record_sql, (migration_id, datetime.now(), migration['description']))
                    sql_executor.DBManager.connection.commit()
                    
                    self.logger.info(f"Migration {migration_id} applied successfully in {duration:.2f} seconds")
                    applied.append(migration_id)
                    
                except Exception as e:
                    sql_executor.DBManager.connection.rollback()
                    self.logger.error(f"Error applying migration {migration_id}: {e}")
                    raise e
                    
            return applied
                
        except Exception as e:
            self.logger.error(f"Migration failed: {e}")
            raise e

    def rollback_migration(self, migration_id: Optional[str] = None) -> List[str]:
        """
        Rolls back the most recent migration or a specific migration if specified.
        
        Args:
            migration_id: Optional specific migration to roll back.
            
        Returns:
            List of rolled back migration IDs.
        """
        self._load_applied_migrations()
        self._scan_available_migrations()
        
        # If no migration specified, get the most recent one
        if not migration_id:
            applied_ids = sorted(self.applied_migrations.keys())
            if not applied_ids:
                self.logger.info("No migrations to roll back")
                return []
            migration_id = applied_ids[-1]
            
        # Check if the migration exists in our records
        if migration_id not in self.applied_migrations:
            self.logger.warning(f"Migration {migration_id} has not been applied")
            return []
            
        if migration_id not in self.available_migrations:
            self.logger.error(f"Cannot roll back migration {migration_id}: migration file not found")
            return []
            
        # Get the migration module
        migration = self.available_migrations[migration_id]
        module = migration["module"]
        
        if not hasattr(module, 'downgrade') or not callable(module.downgrade):
            self.logger.error(f"Migration {migration_id} does not have a downgrade function")
            return []
            
        try:
            self.logger.info(f"Rolling back migration: {migration_id}")
            sql_executor = SQLExecutor("", None)
            cursor = sql_executor.DBManager.cursor
            
            # Apply the downgrade
            module.downgrade(cursor)
            
            # Remove the migration record
            delete_sql = "DELETE FROM schema_migrations WHERE migration_id = %s;"
            cursor.execute(delete_sql, (migration_id,))
            
            sql_executor.DBManager.connection.commit()
            self.logger.info(f"Migration {migration_id} rolled back successfully")
            
            return [migration_id]
            
        except Exception as e:
            self.logger.error(f"Error rolling back migration {migration_id}: {e}")
            raise e

    def get_migration_status(self) -> List[Dict[str, Any]]:
        """
        Returns the status of all migrations.
        
        Returns:
            List of dictionaries with migration information.
        """
        self._load_applied_migrations()
        self._scan_available_migrations()
        
        # Combine all migrations
        all_migrations = sorted(set(list(self.applied_migrations.keys()) + list(self.available_migrations.keys())))
        
        status = []
        for migration_id in all_migrations:
            is_applied = migration_id in self.applied_migrations
            description = ""
            applied_at = None
            
            if is_applied:
                description = self.applied_migrations[migration_id]["description"]
                applied_at = self.applied_migrations[migration_id]["applied_at"]
            elif migration_id in self.available_migrations:
                description = self.available_migrations[migration_id]["description"]
                
            status.append({
                "id": migration_id,
                "is_applied": is_applied,
                "description": description,
                "applied_at": applied_at
            })
            
        return status