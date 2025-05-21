import os
import re
import glob
import time
from datetime import datetime
from mysql.connector import Error
from lib.dbManager import DBManager
from util.logging import log
from util.sqlExecutor import SQLExecutor

class MigrationManager:
    """
    Handles database migrations for the VoxaCommunications-Registry.
    Allows schema evolution without dropping tables.
    """
    def __init__(self, db_manager: DBManager):
        self.logger = log()
        self.logger.info("Migration Manager Initialized")
        self.db_manager = db_manager
        self.migration_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "migrations")
        self.ensure_migration_table_exists()
        
    def ensure_migration_table_exists(self):
        """Ensures the migrations tracking table exists."""
        try:
            sql_executor = SQLExecutor("migrations_table", self.db_manager)
            sql_executor.execute_sql()
            self.logger.info("Migration tracking table is ready")
        except Error as e:
            self.logger.error(f"Failed to create migration tracking table: {e}")
            raise e
    
    def get_applied_migrations(self):
        """Returns a list of migration IDs that have been applied."""
        try:
            query = "SELECT migration_id FROM schema_migrations ORDER BY id;"
            applied = self.db_manager.fetch_all(query)
            return [row[0] for row in applied]
        except Error as e:
            self.logger.error(f"Failed to get applied migrations: {e}")
            return []
    
    def record_migration(self, migration_id, description):
        """Records that a migration has been applied."""
        try:
            query = "INSERT INTO schema_migrations (migration_id, description) VALUES (%s, %s);"
            self.db_manager.execute(query, (migration_id, description))
            self.logger.info(f"Recorded migration {migration_id}")
        except Error as e:
            self.logger.error(f"Failed to record migration {migration_id}: {e}")
            raise e
    
    def remove_migration_record(self, migration_id):
        """Removes a migration record after rollback."""
        try:
            query = "DELETE FROM schema_migrations WHERE migration_id = %s;"
            self.db_manager.execute(query, (migration_id,))
            self.logger.info(f"Removed migration record {migration_id}")
        except Error as e:
            self.logger.error(f"Failed to remove migration record {migration_id}: {e}")
            raise e
    
    def get_pending_migrations(self):
        """Returns a list of migration files that haven't been applied yet."""
        applied_migrations = self.get_applied_migrations()
        all_migrations = self._get_migration_files()
        
        return [m for m in all_migrations if self._get_migration_id_from_filename(m) not in applied_migrations]
    
    def _get_migration_files(self):
        """Returns a list of migration files sorted by version."""
        migration_files = glob.glob(os.path.join(self.migration_dir, "*.sql"))
        # Sort files by the migration version number (timestamp)
        return sorted(migration_files, key=self._get_migration_id_from_filename)
    
    def _get_migration_id_from_filename(self, filename):
        """Extracts the migration ID from a filename."""
        base = os.path.basename(filename)
        match = re.match(r"^(\d+)_.*\.sql$", base)
        if match:
            return match.group(1)
        return base  # Fallback to the filename if pattern doesn't match
    
    def _get_migration_description(self, filename):
        """Extracts a human-readable description from the migration filename."""
        base = os.path.basename(filename)
        match = re.match(r"^\d+_(.*)\.sql$", base)
        if match:
            return match.group(1).replace("_", " ").title()
        return base
    
    def apply_migrations(self):
        """Applies all pending migrations."""
        pending_migrations = self.get_pending_migrations()
        
        if not pending_migrations:
            self.logger.info("No pending migrations to apply.")
            return
        
        total = len(pending_migrations)
        self.logger.info(f"Found {total} pending migrations to apply.")
        
        for i, migration_file in enumerate(pending_migrations, 1):
            migration_id = self._get_migration_id_from_filename(migration_file)
            description = self._get_migration_description(migration_file)
            
            self.logger.info(f"Applying migration {i}/{total}: {description} [{migration_id}]")
            
            try:
                # Execute the migration SQL file
                with open(migration_file, 'r') as f:
                    sql = f.read()
                
                # Split by semicolon to handle multiple statements
                statements = sql.split(';')
                for statement in statements:
                    if statement.strip():
                        self.db_manager.execute(statement)
                
                # Record the migration
                self.record_migration(migration_id, description)
                self.logger.info(f"Successfully applied migration: {description}")
            
            except Exception as e:
                self.logger.error(f"Failed to apply migration {migration_id}: {e}")
                raise e
        
        self.logger.info(f"Successfully applied {total} migrations.")
    
    def create_migration(self, description):
        """Creates a new migration file with the given description."""
        timestamp = int(time.time())
        safe_description = description.lower().replace(" ", "_").replace("-", "_")
        filename = f"{timestamp}_{safe_description}.sql"
        filepath = os.path.join(self.migration_dir, filename)
        
        with open(filepath, 'w') as f:
            f.write(f"-- Migration: {description}\n")
            f.write(f"-- Created at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("-- Write your SQL migration here\n\n")
        
        self.logger.info(f"Created new migration file: {filepath}")
        return filepath